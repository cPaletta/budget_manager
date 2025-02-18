from django.shortcuts import render, redirect, get_object_or_404
from .models import Expense
from .forms import ExpenseForm
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth import logout

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
    expenses = Expense.objects.filter(user=request.user)
    return render(request, 'list.html', {'expenses': expenses})

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