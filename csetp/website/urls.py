from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name="home"),
    path('primm/', views.primm, name="primm"),
    path('database/', views.database_employee, name="employee-list"),
]