import os
import django
import random
from website.models import Employee

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "csetp.settings")
django.setup()

FIRST_NAMES = ["John", "Emma", "Michael", "Sophia", "David", "Olivia", "James", "Ava", "Daniel", "Emily"]
LAST_NAMES = ["Smith", "Johnson", "Brown", "Taylor", "Anderson", "Thomas", "Jackson", "White", "Harris", "Martin"]
EMAIL_DOMAINS = ["company.com", "example.com", "business.org", "corporate.net"]

JOB_TITLES = [
    "Software Engineer", "Data Scientist", "Project Manager",
    "HR Specialist", "Marketing Manager", "Sales Executive"
]

DEPARTMENTS = ["IT", "HR", "Marketing", "Sales", "Finance", "Operations"]

def generate_unique_email(first_name, last_name):
    base_email = f"{first_name.lower()}.{last_name.lower()}@{random.choice(EMAIL_DOMAINS)}"
    email = base_email
    counter = 1

    while Employee.objects.filter(email=email).exists():
        email = f"{first_name.lower()}.{last_name.lower()}{counter}@{random.choice(EMAIL_DOMAINS)}"
        counter += 1

    return email

def populate(n=10):
    for _ in range(n):
        first_name = random.choice(FIRST_NAMES)
        last_name = random.choice(LAST_NAMES)
        email = generate_unique_email(first_name, last_name)
        phone_number = f"555-{random.randint(1000,9999)}"
        job_title = random.choice(JOB_TITLES)
        department = random.choice(DEPARTMENTS)
        salary = round(random.uniform(40000, 120000), 2)

        Employee.objects.create(
            first_name=first_name,
            last_name=last_name,
            email=email,
            phone_number=phone_number,
            job_title=job_title,
            department=department,
            salary=salary,
        )

    print(f"Successfully added {n} employees with unique emails!")

if __name__ == "__main__":
    populate(20)
