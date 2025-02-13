from django.urls import path
from . import views

urlpatterns = [
    path('', views.expense_list, name="expense_list"),
    path('add/', views.add_expense, name="add_expense"),
    path('delete/<int:expense_id>/', views.delete_expense, name="delete_expense"),
]
