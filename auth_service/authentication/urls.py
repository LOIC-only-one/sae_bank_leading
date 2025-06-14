from django.urls import path
from authentication.views import RegisterView, UserDetailView, ResetPasswordView, LoginView, ProfileView, UserListView, UserValidationView, PendingUsersView, logout_view, AgentCreateView, UserDeleteView, validate_token
urlpatterns = [
    # ===== AUTHENTIFICATION =====
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', logout_view, name='logout'),
    path('password/reset/', ResetPasswordView.as_view(), name='password_reset'),

    # ===== PROFIL UTILISATEUR =====
    path('profile/', ProfileView.as_view(), name='profile'),

    # ===== GESTION DES UTILISATEURS (AGENTS) =====
    path('users/<int:user_id>/', UserDetailView.as_view(), name='user_detail'),
    path('users/', UserListView.as_view(), name='user_list'),
    path('users/pending/', PendingUsersView.as_view(), name='pending_users'),
    path('users/<int:user_id>/validate/', UserValidationView.as_view(), name='user_validation'),
    path('users/<int:user_id>/reject/', UserDeleteView.as_view(), name='user_rejection'),
    path('agents/create/', AgentCreateView.as_view(), name='agent_create'),


    # ===== VERFICATION DES TOKENS =====
    path('users/validate-token/', validate_token, name='validate_token'),
]