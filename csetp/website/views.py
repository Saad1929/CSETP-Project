from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from .models import Employee
from django.db import connection


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

@csrf_exempt
def run_modified_query(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            user_query = data.get("query", "").strip()

            # Prevent potentially dangerous queries (Basic protection)
            if any(word in user_query.upper() for word in ["DROP", "DELETE", "UPDATE", "INSERT"]):
                return JsonResponse({"error": "❌ Unsafe query detected. Only SELECT statements are allowed.", "correct": False})

            # Django uses app-based table naming convention, replacing 'employees' with 'website_employee'
            corrected_query = user_query.replace("employees", "website_employee")

            # Execute the user-provided SQL query
            with connection.cursor() as cursor:
                cursor.execute(corrected_query)
                columns = [col[0] for col in cursor.description]  # Get column names
                result = [dict(zip(columns, row)) for row in cursor.fetchall()]

            # Expected correct query result
            expected_result = list(Employee.objects.filter(department="IT").values("first_name", "last_name", "email"))

            # Compare user query result with expected IT department employees
            is_correct = result == expected_result

            return JsonResponse({"result": result, "correct": is_correct})

        except Exception as e:
            return JsonResponse({"error": f"❌ Query Error: {str(e)}", "correct": False})

    return JsonResponse({"error": "❌ Invalid request method.", "correct": False})

@csrf_exempt
def run_make_query(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            user_query = data.get("query", "").strip().lower()

            # The correct answer for the question
            correct_query = 'select * from website_employee where salary < 80000;'

            # Validate MySQL syntax and column names
            with connection.cursor() as cursor:
                try:
                    cursor.execute(user_query)
                except Exception as e:
                    return JsonResponse({"error": f"❌ SQL Syntax Error: {str(e)}", "correct": False})

            # If valid SQL, check if it matches the correct query
            is_correct = user_query.replace(" ", "").replace("\n", "") == correct_query.replace(" ", "").replace("\n", "")

            if is_correct:
                return JsonResponse({"correct": True})  # Will trigger success popup on frontend

            # If incorrect, provide hints
            hint = ""
            if "salary" not in user_query:
                hint = "It looks like you're not filtering by salary."
            elif "<" not in user_query:
                hint = "Are you using the correct comparison operator?"
            elif "website_employee" not in user_query and "from employees" not in user_query:
                hint = "Check your table name. Django may prefix it with the app name."

            return JsonResponse({"correct": False, "hint": hint})

        except Exception as e:
            return JsonResponse({"error": f"❌ Query Execution Error: {str(e)}", "correct": False})

    return JsonResponse({"error": "❌ Invalid request method.", "correct": False})