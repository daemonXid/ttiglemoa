from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.shortcuts import redirect, render
from django.urls import reverse

import json

from .forms import DepositSavingForm, StockHoldingForm, BondHoldingForm
from .models import (
    DepositSaving,
    StockHolding,
    BondHolding,
    DepositValueHistory,
    stock_last_change,
    bond_last_change,
    deposit_last_change,
)


@login_required
def portfolio_index(request):
    deposits = DepositSaving.objects.filter(user=request.user).order_by("-created_at")
    stocks = StockHolding.objects.filter(user=request.user).order_by("-created_at")
    bonds = BondHolding.objects.filter(user=request.user).order_by("-created_at")

    # 통화별 합계 계산 (간단 집계)
    def add_c(map_, currency, amount):
        map_[currency] = map_.get(currency, 0) + float(amount)

    totals_by_currency = {}
    class_totals = {"CASH": 0.0, "STOCK": 0.0, "BOND": 0.0}

    for d in deposits:
        val = d.estimated_value()
        add_c(totals_by_currency, d.currency, val)
        class_totals["CASH"] += float(val)

    for s in stocks:
        val = s.estimated_value()
        add_c(totals_by_currency, s.currency, val)
        class_totals["STOCK"] += float(val)

    for b in bonds:
        val = b.estimated_value()
        add_c(totals_by_currency, b.currency, val)
        class_totals["BOND"] += float(val)

    context = {
        "deposits": deposits,
        "stocks": stocks,
        "bonds": bonds,
        "totals_by_currency": totals_by_currency,
        "class_totals": class_totals,
    }
    return render(request, "tm_assets/portfolio.html", context)


@login_required
def create_deposit(request):
    if request.method == "POST":
        form = DepositSavingForm(request.POST)
        if form.is_valid():
            obj = form.save(commit=False)
            obj.user = request.user
            obj.save()
            messages.success(request, "예적금 항목이 추가되었습니다.")
            return redirect(reverse("tm_assets:portfolio"))
    else:
        form = DepositSavingForm()
    return render(request, "tm_assets/deposit_form.html", {"form": form})


@login_required
def create_stock(request):
    if request.method == "POST":
        form = StockHoldingForm(request.POST)
        if form.is_valid():
            obj = form.save(commit=False)
            obj.user = request.user
            obj.save()
            messages.success(request, "주식 보유내역이 추가되었습니다.")
            return redirect(reverse("tm_assets:portfolio"))
    else:
        form = StockHoldingForm()
    return render(request, "tm_assets/stock_form.html", {"form": form})


@login_required
def create_bond(request):
    if request.method == "POST":
        form = BondHoldingForm(request.POST)
        if form.is_valid():
            obj = form.save(commit=False)
            obj.user = request.user
            obj.save()
            messages.success(request, "채권 보유내역이 추가되었습니다.")
            return redirect(reverse("tm_assets:portfolio"))
    else:
        form = BondHoldingForm()
    return render(request, "tm_assets/bond_form.html", {"form": form})


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
