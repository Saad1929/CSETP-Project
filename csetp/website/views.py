from django.shortcuts import render
from django.http import JsonResponse
from .models import Employee

def home(request):
    return render(request, "home.html", {})

def primm(request):
    return render(request, "primm.html", {})

def database_employee(request):
    employees = Employee.objects.all()
    return render(request, "database.html", {'employees': employees})

def all_questions(request):
    return render(request, "all-questions.html", {})

def primm1(request):
    return render(request, "primm1.html", {})

def run_sql_query(request):
    query_result = list(Employee.objects.filter(job_title="Software Engineer").values("first_name", "last_name", "email", "job_title"))
    return JsonResponse({"result": query_result})