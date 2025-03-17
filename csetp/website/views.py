from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from .models import Employee, Project
from django.db import connection
from django.db.models import Sum
from django.db.models import F




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

def primm2(request):
    return render(request, "primm2.html", {})

def primm3(request):
    return render(request, "primm3.html", {})

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


@csrf_exempt
def run_sql_query_aggregate(request):
    """Executes the COUNT() SQL query and returns the result as JSON."""
    try:
        with connection.cursor() as cursor:
            cursor.execute('SELECT COUNT(email) FROM website_employee WHERE department = "Operations";')
            result = cursor.fetchone()[0]  

        return JsonResponse({"result": result})

    except Exception as e:
        return JsonResponse({"error": f"❌ Query Error: {str(e)}"})
    
@csrf_exempt
def run_modified_query_aggregate(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            user_query = data.get("query", "").strip()

            # Ensure the user query is not empty
            if not user_query:
                return JsonResponse({"error": "❌ Query is empty. Please enter a valid SQL query.", "correct": False})

            # Prevent unsafe queries
            if any(word in user_query.upper() for word in ["DROP", "DELETE", "UPDATE", "INSERT"]):
                return JsonResponse({"error": "❌ Unsafe query detected. Only SELECT statements are allowed.", "correct": False})

            # Correct SQL query
            correct_query = 'SELECT COUNT(email) FROM website_employee WHERE job_title = "Data Scientist";'

            # Replace 'employees' with 'website_employee' (Django ORM uses app name prefix)
            user_query = user_query.replace("employees", "website_employee")

            # Execute user's SQL query
            with connection.cursor() as cursor:
                try:
                    cursor.execute(user_query)
                    result = cursor.fetchone()[0]  # Extract count result
                except Exception as e:
                    return JsonResponse({"error": f"❌ SQL Execution Error: {str(e)}", "correct": False})

            # Expected correct result
            expected_result = Employee.objects.filter(job_title="Data Scientist").count()

            # Compare user result with expected result
            is_correct = result == expected_result

            return JsonResponse({"result": result, "correct": is_correct})

        except Exception as e:
            return JsonResponse({"error": f"❌ Query Processing Error: {str(e)}", "correct": False})

    return JsonResponse({"error": "❌ Invalid request method.", "correct": False})


@csrf_exempt
def run_make_query_aggregate(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            user_query = data.get("query", "").strip()

            # The correct answer for the question
            correct_query = 'SELECT SUM(salary) FROM website_employee WHERE department = "Marketing";'

            # Prevent unsafe queries
            if any(word in user_query.upper() for word in ["DROP", "DELETE", "UPDATE", "INSERT"]):
                return JsonResponse({"error": "❌ Unsafe query detected. Only SELECT statements are allowed.", "correct": False})

            # Replace 'employees' with 'website_employee' (Django ORM uses app name prefix)
            user_query = user_query.replace("employees", "website_employee")

            # Validate SQL syntax
            with connection.cursor() as cursor:
                try:
                    cursor.execute(user_query)
                    result = cursor.fetchone()[0]  # Extract the SUM result
                except Exception as e:
                    return JsonResponse({"error": f"❌ SQL Syntax Error: {str(e)}", "correct": False})

            # Expected correct result
            expected_result = Employee.objects.filter(department="Marketing").aggregate(Sum("salary"))["salary__sum"]

            # Compare user result with expected result
            is_correct = result == expected_result

            # Provide hints if incorrect
            hint = ""
            if "sum" not in user_query.lower():
                hint = "It looks like you're not using SUM()."
            elif "salary" not in user_query.lower():
                hint = "Are you summing the correct column?"
            elif "marketing" not in user_query.lower():
                hint = "Check if you're filtering by the 'Marketing' department."

            return JsonResponse({"correct": is_correct, "hint": hint})

        except Exception as e:
            return JsonResponse({"error": f"❌ Query Processing Error: {str(e)}", "correct": False})

    return JsonResponse({"error": "❌ Invalid request method.", "correct": False})


def database_projects(request):
    projects = Project.objects.all()
    return render(request, "database2.html", {'projects': projects})

@csrf_exempt
def run_sql_query_join(request):
    """Executes an INNER JOIN SQL query and returns the result as JSON."""
    try:
        with connection.cursor() as cursor:
            cursor.execute('''
                SELECT website_employee.first_name, website_employee.last_name, website_project.project_name
                FROM website_employee
                INNER JOIN website_project ON website_employee.id = website_project.employee_id;
            ''')
            columns = [col[0] for col in cursor.description]  # Get column names
            result = [dict(zip(columns, row)) for row in cursor.fetchall()]

        return JsonResponse({"result": result})

    except Exception as e:
        return JsonResponse({"error": f"❌ Query Error: {str(e)}"})
    


@csrf_exempt
def run_modified_query_join(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            user_query = data.get("query", "").strip()

            if not user_query:
                return JsonResponse({"error": "❌ Query is empty. Please enter a valid SQL query.", "correct": False})

            # Prevent unsafe queries
            if any(word in user_query.upper() for word in ["DROP", "DELETE", "UPDATE", "INSERT"]):
                return JsonResponse({"error": "❌ Unsafe query detected. Only SELECT statements are allowed.", "correct": False})

            # Standardizing table names
            corrected_query = (
                user_query
                .replace("employees", "website_employee")
                .replace("projects", "website_project")
            )

            # Execute the user's SQL query
            with connection.cursor() as cursor:
                try:
                    cursor.execute(corrected_query)
                    columns = [col[0] for col in cursor.description]
                    user_result = [dict(zip(columns, row)) for row in cursor.fetchall()]
                except Exception as e:
                    return JsonResponse({"error": f"❌ SQL Execution Error: {str(e)}", "correct": False})

            # Fix the alias issue: Use "expected_project_name" instead of "project_name"
            expected_result = list(
                Project.objects.filter(start_date__gt="2023-01-01")
                .values(
                    first_name=F("employee__first_name"), 
                    last_name=F("employee__last_name"), 
                    expected_project_name=F("project_name")  # Different alias to avoid conflicts
                )
            )

            # Normalize: Convert all values to lowercase strings, remove spaces, and sort both lists
            def normalize_data(data, rename_field=False):
                normalized = []
                for d in data:
                    new_dict = {k: str(v).strip().lower() for k, v in d.items()}
                    if rename_field and "expected_project_name" in new_dict:
                        new_dict["project_name"] = new_dict.pop("expected_project_name")  # Rename back for comparison
                    normalized.append(new_dict)
                return sorted(normalized, key=lambda x: tuple(x.values()))

            user_result_normalized = normalize_data(user_result)
            expected_result_normalized = normalize_data(expected_result, rename_field=True)

            is_correct = user_result_normalized == expected_result_normalized

            return JsonResponse({"result": user_result, "correct": is_correct})

        except json.JSONDecodeError:
            return JsonResponse({"error": "❌ JSON Decode Error: Invalid request format.", "correct": False})
        except Exception as e:
            return JsonResponse({"error": f"❌ Query Processing Error: {str(e)}", "correct": False})

    return JsonResponse({"error": "❌ Invalid request method.", "correct": False})


@csrf_exempt
def run_make_query(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            user_query = data.get("query", "").strip()

            if not user_query:
                return JsonResponse({"error": "❌ Query is empty. Please enter a valid SQL query.", "correct": False})

            # Prevent unsafe queries
            if any(word in user_query.upper() for word in ["DROP", "DELETE", "UPDATE", "INSERT", "ALTER"]):
                return JsonResponse({"error": "❌ Unsafe query detected. Only SELECT statements are allowed.", "correct": False})

            # Debugging: Print the raw user query
            print("🔎 USER QUERY:", user_query)

            # Standardizing table names
            corrected_query = (
                user_query
                .replace("employees", "website_employee")
                .replace("projects", "website_project")
                .replace("employee_email", "employee_id")  # Fix incorrect column references
            )

            # Execute the user's SQL query
            with connection.cursor() as cursor:
                try:
                    cursor.execute(corrected_query)
                    columns = [col[0] for col in cursor.description]
                    user_result = [dict(zip(columns, row)) for row in cursor.fetchall()]
                except Exception as e:
                    return JsonResponse({"error": f"❌ SQL Execution Error: {str(e)}", "correct": False})

            # ✅ Correct Django ORM query to get employees with no projects
            expected_result = list(
                Employee.objects.filter(project__isnull=True)
                .values("first_name", "last_name")
            )

            # 🚀 Debugging: Print both results to check mismatches
            print("🔎 USER QUERY RESULT:", user_result)
            print("🔎 EXPECTED RESULT:", expected_result)

            # Normalize: Convert all values to lowercase strings, remove spaces, and sort both lists
            def normalize_data(data):
                return sorted(
                    [{k: str(v).strip().lower() for k, v in d.items()} for d in data],
                    key=lambda x: tuple(x.values())
                )

            user_result_normalized = normalize_data(user_result)
            expected_result_normalized = normalize_data(expected_result)

            # 🚀 Debugging: Print normalized results
            print("🔎 NORMALIZED USER QUERY RESULT:", user_result_normalized)
            print("🔎 NORMALIZED EXPECTED RESULT:", expected_result_normalized)

            # Check if the results match
            is_correct = user_result_normalized == expected_result_normalized

            # ✅ Custom Hint: If user forgets "IS NULL"
            if not is_correct and "IS NULL" not in user_query.upper():
                return JsonResponse({"error": "❌ Hint: Make sure you use `WHERE projects.employee_email IS NULL`.", "correct": False})

            return JsonResponse({"result": user_result, "correct": is_correct})

        except json.JSONDecodeError:
            return JsonResponse({"error": "❌ JSON Decode Error: Invalid request format.", "correct": False})
        except Exception as e:
            return JsonResponse({"error": f"❌ Query Processing Error: {str(e)}", "correct": False})

    return JsonResponse({"error": "❌ Invalid request method.", "correct": False})