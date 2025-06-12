import requests
from rest_framework.authentication import BaseAuthentication
from rest_framework import exceptions
from django.contrib.auth.models import AnonymousUser
from django.contrib.auth import get_user_model
User = get_user_model()

class RemoteUser:
    """User minimal avec les rôles injectés dans la base de données distantes"""
    def __init__(self, user_id, username, roles):
        self.id = user_id
        self.username = username
        self.roles = roles or []

    def is_authenticated(self):
        return True

    def __str__(self):
        return self.username

class RemoteTokenAuthentication(BaseAuthentication):
    """Authentication backend pour valider les tokens d'authentification
    en interrogeant un service distant. ENTRE AUTH API ET FONCT API"""
    def authenticate(self, request):
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Token '):
            return None

        token = auth_header.split(' ')[1]
        url = 'http://authservice:8000/api/auth/users/validate-token/'
        headers = {'Authorization': f'Token {token}'}

        response = requests.get(url, headers=headers, timeout=5)
        data = response.json()

        user = User(id=data['user_id'], username=data['username'])
        user.roles = [data.get('role', '').lower()]

        return (user, None)
