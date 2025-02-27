from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from .models import Expense
from datetime import datetime

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

    def test_invalid_form_submission(self):
        response = self.client.post(reverse('add_expense'), {
            'date': '',
            'category': '',
            'title': '',  
            'currency': '',
            'amount': ''
        })
        self.assertEqual(response.status_code, 200)
        form = response.context['form']
        self.assertTrue(form.errors)
        # self.assertIn('date', form.errors)
        # self.assertIn('category', form.errors)
        # self.assertIn('title', form.errors)
        # self.assertIn('currency', form.errors)
        # self.assertIn('amount', form.errors)
