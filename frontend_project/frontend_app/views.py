import requests
from django.shortcuts import render, redirect
from django.contrib import messages

AUTH_API_URL = 'http://127.0.0.1:8000'

def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        response = requests.post(f"{AUTH_API_URL}/api/auth/login/", json={
            'username': username,
            'password': password
        })

        if response.status_code == 200:
            response_data = response.json()
            request.session['token'] = response_data['token']
            request.session['user'] = response_data['user']
            return render(request, 'frontend_app/home.html', {'user': response_data['user']})
        else:
            messages.error(request, "Identifiants invalides.")

    return render(request, 'frontend_app/login.html')


def logout_view(request):
    request.session.flush()
    return redirect('login')
