from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User

def register_view(request):
    error = None

    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        if User.objects.filter(username=username).exists():
            error = "Ce nom d'utilisateur existe déjà."
        else:
            User.objects.create_user(username=username, password=password)
            return redirect("accounts:login")

    return render(request, "register.html", {"error": error})


def login_view(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect("chat:home")

    return render(request, "login.html")


def logout_view(request):
    logout(request)
    return redirect("/")
