from django import forms

from .models import DepositSaving, StockHolding, BondHolding


class DepositSavingForm(forms.ModelForm):
    class Meta:
        model = DepositSaving
        fields = [
            "product_type",
            "bank_name",
            "product_name",
            "principal_amount",
            "annual_rate",
            "compounding",
            "start_date",
            "maturity_date",
            "currency",
            "current_value_manual",
        ]
        labels = {
            "product_type": "유형",
            "bank_name": "은행명",
            "product_name": "상품명",
            "principal_amount": "원금",
            "annual_rate": "연이율(%)",
            "compounding": "복리 주기",
            "start_date": "시작일",
            "maturity_date": "만기일",
            "currency": "통화",
            "current_value_manual": "평가액(직접입력)",
        }
        widgets = {
            "bank_name": forms.TextInput(attrs={"placeholder": "예: 국민은행"}),
            "product_name": forms.TextInput(attrs={"placeholder": "예: 정기예금"}),
            "principal_amount": forms.NumberInput(attrs={"placeholder": "예: 10000000"}),
            "annual_rate": forms.NumberInput(attrs={"step": "0.01", "placeholder": "예: 3.5"}),
            "start_date": forms.DateInput(attrs={"type": "date"}),
            "maturity_date": forms.DateInput(attrs={"type": "date"}),
            "current_value_manual": forms.NumberInput(attrs={"placeholder": "선택 입력"}),
        }


class StockHoldingForm(forms.ModelForm):
    class Meta:
        model = StockHolding
        fields = [
            "market",
            "ticker",
            "name",
            "quantity",
            "average_price",
            "currency",
            "current_price",
        ]
        labels = {
            "market": "시장",
            "ticker": "티커/종목코드",
            "name": "종목명",
            "quantity": "수량",
            "average_price": "평단가",
            "currency": "통화",
            "current_price": "현재가",
        }
        widgets = {
            "ticker": forms.TextInput(attrs={"placeholder": "국내: 6자리 코드, 해외: 심볼"}),
            "name": forms.TextInput(attrs={"placeholder": "예: 삼성전자 / Apple Inc."}),
            "quantity": forms.NumberInput(attrs={"step": "0.0001"}),
            "average_price": forms.NumberInput(attrs={"step": "0.0001"}),
            "current_price": forms.NumberInput(attrs={"step": "0.0001", "placeholder": "선택 입력"}),
        }


class BondHoldingForm(forms.ModelForm):
    class Meta:
        model = BondHolding
        fields = [
            "name",
            "issuer",
            "currency",
            "face_amount",
            "coupon_rate",
            "purchase_price_pct",
            "current_price_pct",
            "maturity_date",
            "bond_code",
        ]
        labels = {
            "name": "채권명",
            "issuer": "발행처",
            "currency": "통화",
            "face_amount": "액면총액",
            "coupon_rate": "표면금리(%)",
            "purchase_price_pct": "매수가(%)",
            "current_price_pct": "현재가(%)",
            "maturity_date": "만기일",
            "bond_code": "채권코드",
        }
        widgets = {
            "maturity_date": forms.DateInput(attrs={"type": "date"}),
            "name": forms.TextInput(attrs={"placeholder": "예: 국고채 3년"}),
            "issuer": forms.TextInput(attrs={"placeholder": "예: 대한민국"}),
            "face_amount": forms.NumberInput(attrs={"placeholder": "예: 10000000"}),
            "coupon_rate": forms.NumberInput(attrs={"step": "0.01", "placeholder": "예: 3.2"}),
            "purchase_price_pct": forms.NumberInput(attrs={"step": "0.001", "placeholder": "예: 98.500"}),
            "current_price_pct": forms.NumberInput(attrs={"step": "0.001", "placeholder": "선택 입력"}),
            "bond_code": forms.TextInput(attrs={"placeholder": "pykrx 조회용 KRX/ISIN 코드"}),
        }
