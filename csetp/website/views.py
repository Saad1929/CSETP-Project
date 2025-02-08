from django.shortcuts import render

def home(request):
    return render(request, "home.html", {})

def primm(request):
    return render(request, "primm.html", {})
