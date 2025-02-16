from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name="home"),
    path('primm/', views.primm, name="primm"),
    path('database/', views.database_employee, name="employee-list"),
    path('all-questions/', views.all_questions, name="all-questions"), 
    path('primm1/', views.primm1, name="primm1"),
    path('run-sql-query/', views.run_sql_query, name="run_sql_query"),
]