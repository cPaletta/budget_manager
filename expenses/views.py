from django.shortcuts import render, redirect, get_object_or_404
from .models import Expense
from .forms import ExpenseForm
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth import logout
from django.db.models import Sum
from django.db.models.functions import TruncMonth
from datetime import datetime

@login_required
def add_expense(request):
    if request.method == 'POST':
        form = ExpenseForm(request.POST)
        if form.is_valid():
            expense = form.save(commit=False)
            expense.user = request.user
            expense.save()
            return redirect('expense_list')
    else:
        form = ExpenseForm()
    return render(request, 'add.html', {'form': form})

@login_required
def expense_list(request):
    selected_year = int(request.GET.get('year', datetime.now().year))
    expenses = Expense.objects.filter(user=request.user, date__year=selected_year)
    monthly_totals = expenses.annotate(month=TruncMonth('date')).values('month').annotate(total=Sum('amount')).order_by('month')
    
    # Create a list of tuples with all months of the selected year
    all_months = [(datetime(selected_year, month, 1), 0) for month in range(1, 13)]
    for total in monthly_totals:
        for i, (month, _) in enumerate(all_months):
            if month.month == total['month'].month:
                all_months[i] = (month, total['total'])
    
    years = Expense.objects.filter(user=request.user).dates('date', 'year')
    return render(request, 'list.html', {'expenses': expenses, 'monthly_totals': all_months, 'years': years, 'selected_year': selected_year})

@login_required
def delete_expense(request, expense_id):
    expense = get_object_or_404(Expense, id=expense_id, user=request.user)
    if request.method == 'POST':
        expense.delete()
        messages.success(request, 'Expense deleted successfully.')
        return redirect('expense_list')
    return render(request, 'confirm_delete.html', {'expense': expense})

def custom_logout(request):
    if request.method == 'POST':
        logout(request)
        return redirect('account_login')
    return redirect('account_login')

def home(request):
    return render(request, 'home.html')