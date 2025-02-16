from django.shortcuts import render
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

