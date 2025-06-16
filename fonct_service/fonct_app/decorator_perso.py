import requests
from rest_framework.authentication import BaseAuthentication
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


from rest_framework.response import Response

def agent_required(view_func):
    def decorated_view(request, *args, **kwargs):
        roles = getattr(request.user, 'roles', [])
        for r in roles:
            if r.lower() == 'agent':
                return view_func(request, *args, **kwargs)
        return Response({"error": "Accès interdit : vous devez être agent."}, status=403)
    return decorated_view