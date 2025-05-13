from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from .models import Expense
from .forms import ExpenseForm
from datetime import datetime
from decimal import Decimal

class ExpenseModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpassword')
        self.expense = Expense.objects.create(
            user=self.user,
            date=datetime.now(),
            category='Food',
            amount=100.00
        )

    def test_expense_creation(self):
        self.assertEqual(self.expense.user.username, 'testuser')
        self.assertEqual(self.expense.category, 'Food')
        self.assertEqual(self.expense.amount, 100.00)

class ExpenseViewsTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='testpassword')
        self.client.login(username='testuser', password='testpassword')
        self.expense = Expense.objects.create(
            user=self.user,
            date=datetime.now(),
            category='Food',
            amount=100.00
        )

    def test_expense_list_view(self):
        response = self.client.get(reverse('expense_list'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'list.html')
        self.assertContains(response, 'Your expenses')

    def test_add_expense_view(self):
        response = self.client.get(reverse('add_expense'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'add.html')

        response = self.client.post(reverse('add_expense'), {
            'date': datetime.now().strftime('%Y-%m-%d'),
            'category': 'Transport',
            'title': 'Taxi Ride',  
            'currency': 'PLN',
            'amount': 50.00
        })
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('expense_list'))
        self.assertEqual(Expense.objects.count(), 2)

    def test_delete_expense_view(self):
        response = self.client.post(reverse('delete_expense', args=[self.expense.id]))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('expense_list'))
        self.assertEqual(Expense.objects.count(), 0)

    def test_unauthenticated_access(self):
        self.client.logout()
        response = self.client.get(reverse('expense_list'))
        self.assertRedirects(response, '/accounts/login/?next=/expenses/')
        
    def test_monthly_totals_calculation(self):
        Expense.objects.filter(user=self.user).delete() 

        current_year = datetime.now().year
        # January expenses
        Expense.objects.create(
            user=self.user, date=datetime(current_year, 1, 10), category='Food', title='Groceries Jan', currency='PLN', amount=Decimal('100.00')
        )
        Expense.objects.create(
            user=self.user, date=datetime(current_year, 1, 15), category='Food', title='Restaurant Jan', currency='PLN', amount=Decimal('50.00')
        ) # Total Jan: 150.00

        # February expenses
        Expense.objects.create(
            user=self.user, date=datetime(current_year, 2, 5), category='Transport', title='Bus Feb', currency='PLN', amount=Decimal('20.00')
        ) # Total Feb: 20.00

        response = self.client.get(reverse('expense_list') + f'?year={current_year}')
        self.assertEqual(response.status_code, 200)

        all_months_data = response.context['monthly_totals']

        jan_total = Decimal('0.00')
        for month_dt, total in all_months_data:
            if month_dt.year == current_year and month_dt.month == 1:
                jan_total = total
                break
        self.assertEqual(jan_total, Decimal('150.00'))

        feb_total = Decimal('0.00')
        for month_dt, total in all_months_data:
            if month_dt.year == current_year and month_dt.month == 2:
                feb_total = total
                break
        self.assertEqual(feb_total, Decimal('20.00'))

        mar_total = Decimal('0.00') # Month with no expenses
        for month_dt, total in all_months_data:
            if month_dt.year == current_year and month_dt.month == 3:
                mar_total = total
                break
        self.assertEqual(mar_total, Decimal('0.00'))


    def test_sum_expenses_for_different_months(self):
        Expense.objects.filter(user=self.user).delete() # Clean slate

        current_year = datetime.now().year
        # April expenses
        Expense.objects.create(
            user=self.user, date=datetime(current_year, 4, 5), category='Entertainment', title='Cinema', currency='PLN', amount=Decimal('30.00')
        )
        Expense.objects.create(
            user=self.user, date=datetime(current_year, 4, 15), category='Entertainment', title='Concert', currency='PLN', amount=Decimal('120.00')
        ) # Total April: 150.00

        # May expenses
        Expense.objects.create(
            user=self.user, date=datetime(current_year, 5, 10), category='Bills', title='Electricity', currency='PLN', amount=Decimal('200.00')
        ) # Total May: 200.00

        response = self.client.get(reverse('expense_list') + f'?year={current_year}')
        self.assertEqual(response.status_code, 200)

        monthly_totals = response.context['monthly_totals']
        
        totals_map = {month_dt.month: total for month_dt, total in monthly_totals if month_dt.year == current_year}

        self.assertEqual(totals_map.get(4, Decimal('0.00')), Decimal('150.00'))
        self.assertEqual(totals_map.get(5, Decimal('0.00')), Decimal('200.00'))
        self.assertEqual(totals_map.get(6, Decimal('0.00')), Decimal('0.00')) # Check a month with no expenses


class ExpenseFormTest(TestCase):
    def test_expense_form_valid(self):
        form_data = {
            'date': datetime.now().strftime('%Y-%m-%d'),
            'category': 'Food',
            'title': 'Dinner',
            'currency': 'PLN',
            'amount': 100.00
        }
        form = ExpenseForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_expense_form_invalid_empty_fields(self):
        form_data = {
            'date': '',
            'category': '',
            'title': '',  
            'currency': '',
            'amount': ''
        }
        form = ExpenseForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('date', form.errors)
        self.assertIn('category', form.errors)
        self.assertIn('title', form.errors)
        self.assertIn('currency', form.errors)
        self.assertIn('amount', form.errors)

    def test_expense_form_invalid_amount_zero(self):
        form_data = {
            'date': datetime.now().strftime('%Y-%m-%d'),
            'category': 'Food',
            'title': 'Dinner',
            'currency': 'PLN',
            'amount': 0
        }
        form = ExpenseForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('amount', form.errors)
        self.assertEqual(form.errors['amount'][0], "Amount must be greater than 0.")

    def test_expense_form_invalid_amount_negative(self):
        form_data = {
            'date': datetime.now().strftime('%Y-%m-%d'),
            'category': 'Food',
            'title': 'Dinner',
            'currency': 'PLN',
            'amount': -10
        }
        form = ExpenseForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('amount', form.errors)
        self.assertEqual(form.errors['amount'][0], "Amount must be greater than 0.")
    
    def test_expense_form_invalid_date_format(self):
        form_data = {
            'date': 'invalid-date',
            'category': 'Food',
            'title': 'Dinner',
            'currency': 'PLN',
            'amount': 100.00
        }
        form = ExpenseForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('date', form.errors)

