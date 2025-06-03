import requests
from django.shortcuts import render, redirect

API_URL_AUTH = 'http://127.0.0.1:8000/api/auth/'

def login_view(request):

    return render(request, 'frontend_app/login.html')


def home_view(request):
    return render(request, 'frontend_app/home.html')


def logout_view(request):
    return redirect('login')
