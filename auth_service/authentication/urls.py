# authentication/urls.py
from django.urls import path

from authentication.views import RegisterView, LoginView, ProfileView, UserListView, UserValidationView, PendingUsersView, logout_view, AgentCreateView


from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

urlpatterns = [
    # ===== AUTHENTIFICATION =====

    # Authentification via JWT
    path('jwt/login/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('jwt/refresh/', TokenRefreshView.as_view(), name='token_refresh'),


    path('register/', RegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', logout_view, name='logout'),
    
    # ===== PROFIL UTILISATEUR =====
    path('profile/', ProfileView.as_view(), name='profile'),
    
    # ===== GESTION DES UTILISATEURS (AGENTS) =====
    path('users/', UserListView.as_view(), name='user_list'),
    path('users/pending/', PendingUsersView.as_view(), name='pending_users'),
    path('users/<int:user_id>/validate/', UserValidationView.as_view(), name='user_validation'),
    path('agents/create/', AgentCreateView.as_view(), name='agent-create'),
]
