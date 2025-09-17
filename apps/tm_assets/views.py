from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.shortcuts import redirect, render, get_object_or_404
from django.urls import reverse
from django.http import HttpResponseForbidden, HttpResponseNotAllowed
from django.utils import timezone
from django.db.models import Q
from django.views.generic import CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy

import json
from datetime import timedelta, date
from collections import defaultdict
from typing import Dict, List, Any, Tuple
from decimal import Decimal

from .forms import DepositSavingForm, StockHoldingForm, BondHoldingForm
from .models import (
    DepositSaving,
    StockHolding,
    BondHolding,
    DepositValueHistory,
    StockPriceHistory,
    BondPriceHistory,
    stock_last_change,
    bond_last_change,
    deposit_last_change,
)


def _valuation_class(current, baseline):
    """Return bootstrap text class based on valuation result."""
    if current is None or baseline is None:
        return ""
    if current > baseline:
        return "text-danger"
    if current < baseline:
        return "text-primary"
    return ""


def get_portfolio_history(user, days: int = 90) -> List[Dict[str, Any]]:
    """사용자의 포트폴리오 히스토리 데이터를 생성합니다.

    Args:
        user: Django User 인스턴스
        days: 히스토리를 조회할 일수 (기본 90일)

    Returns:
        날짜별 자산 가치 히스토리 리스트
    """
    end_date = timezone.localdate()
    start_date = end_date - timedelta(days=days)

    # 사용자의 모든 자산 조회
    deposits = DepositSaving.objects.filter(user=user)
    stocks = StockHolding.objects.filter(user=user)
    bonds = BondHolding.objects.filter(user=user)

    # 히스토리 데이터 조회
    deposit_histories = DepositValueHistory.objects.filter(
        deposit__user=user,
        recorded_at__date__gte=start_date
    ).order_by('recorded_at')

    stock_histories = StockPriceHistory.objects.filter(
        stock__user=user,
        recorded_at__date__gte=start_date
    ).order_by('recorded_at')

    bond_histories = BondPriceHistory.objects.filter(
        bond__user=user,
        recorded_at__date__gte=start_date
    ).order_by('recorded_at')

    # 날짜별 데이터 집계
    daily_data = defaultdict(lambda: {
        'deposit_value': 0,
        'stock_value': 0,
        'bond_value': 0,
        'total_value': 0
    })

    # 예적금 히스토리 처리
    for history in deposit_histories:
        day = history.recorded_at.date()
        daily_data[day]['deposit_value'] += float(history.value)

    # 주식 히스토리 처리
    for history in stock_histories:
        day = history.recorded_at.date()
        stock_value = float(history.price) * float(history.stock.quantity)
        daily_data[day]['stock_value'] += stock_value

    # 채권 히스토리 처리
    for history in bond_histories:
        day = history.recorded_at.date()
        bond_value = float(history.bond.face_amount) * (float(history.price_pct) / 100)
        daily_data[day]['bond_value'] += bond_value

    # 히스토리 데이터가 없을 경우 현재 데이터를 기반으로 샘플 생성
    if not daily_data and (deposits.exists() or stocks.exists() or bonds.exists()):
        current_deposit_value = sum(float(d.estimated_value()) for d in deposits)
        current_stock_value = sum(float(s.estimated_value()) for s in stocks)
        current_bond_value = sum(float(b.estimated_value()) for b in bonds)

        # 지난 30일간 샘플 데이터 생성 (약간의 변동 추가)
        import random
        for i in range(min(days, 30)):
            sample_date = end_date - timedelta(days=i)
            # 약간의 랜덤 변동 (±5%) 추가
            variation = 1 + (random.random() - 0.5) * 0.1  # -5% ~ +5%

            daily_data[sample_date] = {
                'deposit_value': current_deposit_value * variation,
                'stock_value': current_stock_value * variation,
                'bond_value': current_bond_value * variation,
                'total_value': 0
            }

    # 총합 계산 및 정렬
    portfolio_history = []
    for day in sorted(daily_data.keys()):
        data = daily_data[day]
        data['total_value'] = data['deposit_value'] + data['stock_value'] + data['bond_value']
        portfolio_history.append({
            'date': day.isoformat(),
            'deposit_value': round(data['deposit_value'], 2),
            'stock_value': round(data['stock_value'], 2),
            'bond_value': round(data['bond_value'], 2),
            'total_value': round(data['total_value'], 2)
        })

    return portfolio_history


def calculate_asset_totals(user) -> Tuple[Dict[str, float], Dict[str, float]]:
    """사용자의 자산 합계를 계산합니다.

    Returns:
        (통화별 합계, 자산 클래스별 합계) 튜플
    """
    # 한 번의 쿼리로 모든 데이터 가져오기 (select_related 없이도 외래키 참조 없음)
    deposits = DepositSaving.objects.filter(user=user).only(
        'currency', 'principal_amount', 'annual_rate', 'compounding',
        'start_date', 'maturity_date', 'current_value_manual'
    )
    stocks = StockHolding.objects.filter(user=user).only(
        'currency', 'quantity', 'average_price', 'current_price'
    )
    bonds = BondHolding.objects.filter(user=user).only(
        'currency', 'face_amount', 'purchase_price_pct', 'current_price_pct'
    )

    totals_by_currency = defaultdict(float)
    class_totals = {"CASH": 0.0, "STOCK": 0.0, "BOND": 0.0}

    # 예적금 집계
    for deposit in deposits:
        val = float(deposit.estimated_value())
        totals_by_currency[deposit.currency] += val
        class_totals["CASH"] += val

    # 주식 집계
    for stock in stocks:
        val = float(stock.estimated_value())
        totals_by_currency[stock.currency] += val
        class_totals["STOCK"] += val

    # 채권 집계
    for bond in bonds:
        val = float(bond.estimated_value())
        totals_by_currency[bond.currency] += val
        class_totals["BOND"] += val

    return dict(totals_by_currency), class_totals


@login_required
def portfolio_index(request):
    """포트폴리오 메인 화면"""
    deposits = list(
        DepositSaving.objects.filter(user=request.user).order_by("-created_at")
    )
    stocks = list(
        StockHolding.objects.filter(user=request.user).order_by("-created_at")
    )
    for stock in stocks:
        estimated_total = stock.estimated_value()
        purchase_total = stock.purchase_value
        stock.estimated_total = estimated_total
        stock.purchase_total = purchase_total
        stock.valuation_class = _valuation_class(estimated_total, purchase_total)

    bonds = list(
        BondHolding.objects.filter(user=request.user).order_by("-created_at")
    )
    for bond in bonds:
        estimated_total = bond.estimated_value()
        purchase_total = bond.face_amount * (bond.purchase_price_pct / Decimal("100"))
        bond.estimated_total = estimated_total
        bond.purchase_total = purchase_total
        bond.valuation_class = _valuation_class(estimated_total, purchase_total)

    totals_by_currency, class_totals = calculate_asset_totals(request.user)
    portfolio_history = get_portfolio_history(request.user, days=90)

    context = {
        "deposits": deposits,
        "stocks": stocks,
        "bonds": bonds,
        "totals_by_currency": totals_by_currency,
        "class_totals": class_totals,
        "portfolio_history": portfolio_history,
    }
    return render(request, "tm_assets/portfolio.html", context)


# =============================================================================
# 공통 CRUD 헬퍼 함수들
# =============================================================================

def _get_asset_config(asset_type: str) -> Dict[str, Any]:
    """자산 타입별 설정을 반환합니다."""
    configs = {
        'deposit': {
            'model': DepositSaving,
            'form': DepositSavingForm,
            'template': 'tm_assets/asset_form.html',
            'name': '예적금',
        },
        'stock': {
            'model': StockHolding,
            'form': StockHoldingForm,
            'template': 'tm_assets/asset_form.html',
            'name': '주식',
        },
        'bond': {
            'model': BondHolding,
            'form': BondHoldingForm,
            'template': 'tm_assets/asset_form.html',
            'name': '채권',
        }
    }
    return configs.get(asset_type, {})


def _create_asset(request, asset_type: str):
    """공통 자산 생성 뷰"""
    config = _get_asset_config(asset_type)
    if not config:
        return HttpResponseForbidden()

    if request.method == "POST":
        form = config['form'](request.POST)
        if form.is_valid():
            obj = form.save(commit=False)
            obj.user = request.user
            obj.save()
            messages.success(request, f"{config['name']} 항목이 추가되었습니다.")
            return redirect(reverse("tm_assets:portfolio"))
    else:
        form = config['form']()

    context = {
        'form': form,
        'asset_type': asset_type,
        'asset_name': config['name'],
        'action': 'create'
    }
    return render(request, config['template'], context)


def _edit_asset(request, asset_type: str, pk: int):
    """공통 자산 수정 뷰"""
    config = _get_asset_config(asset_type)
    if not config:
        return HttpResponseForbidden()

    obj = get_object_or_404(config['model'], pk=pk, user=request.user)

    if request.method == "POST":
        form = config['form'](request.POST, instance=obj)
        if form.is_valid():
            form.save()
            messages.success(request, f"{config['name']} 항목이 수정되었습니다.")
            return redirect(reverse("tm_assets:portfolio"))
    else:
        form = config['form'](instance=obj)

    context = {
        'form': form,
        'asset_type': asset_type,
        'asset_name': config['name'],
        'action': 'edit',
        'object': obj
    }
    return render(request, config['template'], context)


def _delete_asset(request, asset_type: str, pk: int):
    """공통 자산 삭제 뷰"""
    if request.method != "POST":
        return HttpResponseNotAllowed(["POST"])

    config = _get_asset_config(asset_type)
    if not config:
        return HttpResponseForbidden()

    obj = get_object_or_404(config['model'], pk=pk, user=request.user)
    obj.delete()
    messages.success(request, f"{config['name']} 항목이 삭제되었습니다.")
    return redirect(reverse("tm_assets:portfolio"))


# =============================================================================
# 예적금 뷰들
# =============================================================================

@login_required
def create_deposit(request):
    return _create_asset(request, 'deposit')


@login_required
def edit_deposit(request, pk):
    return _edit_asset(request, 'deposit', pk)


@login_required
def delete_deposit(request, pk):
    return _delete_asset(request, 'deposit', pk)


# =============================================================================
# 주식 뷰들
# =============================================================================

@login_required
def create_stock(request):
    return _create_asset(request, 'stock')


@login_required
def edit_stock(request, pk):
    return _edit_asset(request, 'stock', pk)


@login_required
def delete_stock(request, pk):
    return _delete_asset(request, 'stock', pk)


# =============================================================================
# 채권 뷰들
# =============================================================================

@login_required
def create_bond(request):
    return _create_asset(request, 'bond')


@login_required
def edit_bond(request, pk):
    return _edit_asset(request, 'bond', pk)


@login_required
def delete_bond(request, pk):
    return _delete_asset(request, 'bond', pk)


@login_required
def refresh_prices(request):
    updated_s = updated_b = 0
    for s in StockHolding.objects.filter(user=request.user):
        if s.update_price_via_fdr():
            updated_s += 1
    for b in BondHolding.objects.filter(user=request.user):
        if b.update_price_via_pykrx():
            updated_b += 1
    # 예적금은 평가액 스냅샷 저장
    deposits = DepositSaving.objects.filter(user=request.user)
    now = None
    for d in deposits:
        val = d.estimated_value()
        try:
            # 같은 시각 중복 저장 방지까지는 두지 않음(간단 구현)
            DepositValueHistory.objects.create(deposit=d, value=val)
        except Exception:
            pass
    messages.info(request, f"가격 업데이트 완료 - 주식 {updated_s} / 채권 {updated_b}")
    return redirect(reverse("tm_assets:portfolio"))


# ----- New pages: allocation + details -----

@login_required
def allocation(request):
    deposits = DepositSaving.objects.filter(user=request.user)
    stocks = StockHolding.objects.filter(user=request.user)
    bonds = BondHolding.objects.filter(user=request.user)

    class_totals = {
        "예적금": sum(float(d.estimated_value()) for d in deposits),
        "주식": sum(float(s.estimated_value()) for s in stocks),
        "채권": sum(float(b.estimated_value()) for b in bonds),
    }
    total_sum = sum(class_totals.values()) or 0.0
    if total_sum > 0:
        class_ratios = {k: round(v * 100.0 / total_sum, 2) for k, v in class_totals.items()}
    else:
        class_ratios = {k: 0 for k in class_totals.keys()}

    class_items = [
        {"label": k, "ratio": class_ratios[k], "total": class_totals[k]}
        for k in ["예적금", "주식", "채권"]
    ]

    # 통화별 비중도 함께 제공
    currency_totals = {}
    for d in deposits:
        currency_totals[d.currency] = currency_totals.get(d.currency, 0.0) + float(d.estimated_value())
    for s in stocks:
        currency_totals[s.currency] = currency_totals.get(s.currency, 0.0) + float(s.estimated_value())
    for b in bonds:
        currency_totals[b.currency] = currency_totals.get(b.currency, 0.0) + float(b.estimated_value())
    currency_ratios = (
        {k: round(v * 100.0 / total_sum, 2) for k, v in currency_totals.items()} if total_sum > 0 else {}
    )
    currency_items = [
        {"label": k, "ratio": currency_ratios.get(k, 0), "total": v}
        for k, v in currency_totals.items()
    ]

    class_json_labels = json.dumps([i["label"] for i in class_items], ensure_ascii=False)
    class_json_data = json.dumps([i["ratio"] for i in class_items])
    currency_json_labels = json.dumps([i["label"] for i in currency_items], ensure_ascii=False)
    currency_json_data = json.dumps([i["ratio"] for i in currency_items])

    # 변동 합계(간단 합산)
    cash_change = sum((deposit_last_change(d)[0] or 0.0) for d in deposits)
    stock_change = sum(((stock_last_change(s)[0] or 0.0) * float(s.quantity)) for s in stocks)
    bond_change = sum((float(b.face_amount) * (bond_last_change(b)[0] or 0.0) / 100.0) for b in bonds)
    class_change_sums = {"CASH": cash_change, "STOCK": stock_change, "BOND": bond_change}

    context = {
        "class_items": class_items,
        "currency_items": currency_items,
        "class_json_labels": class_json_labels,
        "class_json_data": class_json_data,
        "currency_json_labels": currency_json_labels,
        "currency_json_data": currency_json_data,
        "class_change_sums": class_change_sums,
        "total_sum": total_sum,
    }
    return render(request, "tm_assets/allocation.html", context)


@login_required
def deposits_list(request):
    deposits = DepositSaving.objects.filter(user=request.user).order_by("-created_at")
    total = sum(float(d.estimated_value()) for d in deposits)
    # 변동 합계
    change_sum = 0.0
    for d in deposits:
        delta, _ = deposit_last_change(d)
        if delta is not None:
            change_sum += float(delta)
    return render(
        request,
        "tm_assets/deposits_list.html",
        {"deposits": deposits, "total": total, "change_sum": change_sum},
    )


@login_required
def stocks_list(request):
    stocks = StockHolding.objects.filter(user=request.user).order_by("-created_at")
    total = sum(float(s.estimated_value()) for s in stocks)
    change_sum = 0.0
    for s in stocks:
        delta, pct = stock_last_change(s)
        if delta is not None:
            # 평가액 기준 변동 = 가격변동 * 수량
            change_sum += float(delta) * float(s.quantity)
    return render(
        request,
        "tm_assets/stocks_list.html",
        {"stocks": stocks, "total": total, "change_sum": change_sum},
    )


@login_required
def bonds_list(request):
    bonds = BondHolding.objects.filter(user=request.user).order_by("-created_at")
    total = sum(float(b.estimated_value()) for b in bonds)
    change_sum = 0.0
    for b in bonds:
        delta_pct, _ = bond_last_change(b)
        if delta_pct is not None:
            # 평가액 기준 변동 = 액면총액 * (delta_pct/100)
            change_sum += float(b.face_amount) * float(delta_pct) / 100.0
    return render(
        request,
        "tm_assets/bonds_list.html",
        {"bonds": bonds, "total": total, "change_sum": change_sum},
    )
