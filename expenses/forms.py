from django import forms
from .models import Expense
from django.core.exceptions import ValidationError

class ExpenseForm(forms.ModelForm):
    class Meta:
        model = Expense
        fields = ["title", "amount", "category", "date", "currency"]
        widgets = {
            "date": forms.DateInput(attrs={"type": "date"})  
        }

    def clean_amount(self):
        amount = self.cleaned_data.get("amount")
        if amount is not None and amount <= 0:
            raise ValidationError("Amount must be greater than 0.")
        return amount
