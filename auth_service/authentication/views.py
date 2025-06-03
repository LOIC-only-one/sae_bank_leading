from rest_framework import status, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.views import APIView
from django.contrib.auth import get_user_model, login, logout
from django.shortcuts import get_object_or_404
from .serializers import RegisterSerializer, LoginSerializer, UserProfileSerializer, UserListSerializer, UserValidationSerializer


User = get_user_model()

class RegisterView(APIView):
    """
    RegisterView(APIView)
    ---------------------
    Vue d'API permettant à un utilisateur de s'inscrire.

    POST:
        Crée un nouveau compte utilisateur.
        - Permissions : Accessible à tous.
        - Corps de la requête : { "username": str, "email": str, "password": str, ... }
        - Réponses :
            - 201 : Compte créé avec succès, retourne les informations de l'utilisateur.
            - 400 : Erreur de validation.
    """
    permission_classes = [permissions.AllowAny]
    def post(self, request):
        serializer = RegisterSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            user = serializer.save()
            return Response({'message': 'Compte créé avec succès', 'user': {'id': user.id, 'username': user.username, 'email': user.email, 'role': user.role, 'is_active': user.is_active}}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class LoginView(APIView):
    """
    LoginView(APIView)
    ------------------
    Vue d'API permettant à un utilisateur de se connecter.

    POST:
        Authentifie un utilisateur avec ses identifiants.
        - Permissions : Accessible à tous.
        - Corps de la requête : { "username": str, "password": str }
        - Réponses :
            - 200 : Connexion réussie, retourne les informations de l'utilisateur.
            - 400 : Erreur de validation ou identifiants invalides.
    """
    permission_classes = [permissions.AllowAny]
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data['user']
            login(request, user)
            return Response({'message': 'Connexion réussie', 'user': {'id': user.id, 'username': user.username, 'email': user.email, 'role': user.role, 'role_display': user.get_role_display(), 'is_active': user.is_active}}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ProfileView(APIView):
    """
    ProfileView(APIView)
    --------------------
    Vue d'API permettant à un utilisateur authentifié de consulter ou modifier son profil.

    GET:
        Retourne les informations du profil de l'utilisateur connecté.
        - Permissions : Authentification requise.
        - Réponses :
            - 200 : Données du profil utilisateur.

    PUT:
        Met à jour les informations du profil de l'utilisateur connecté.
        - Permissions : Authentification requise.
        - Corps de la requête : Champs du profil à modifier.
        - Réponses :
            - 200 : Profil mis à jour avec succès.
            - 400 : Erreur de validation.
    """
    permission_classes = [permissions.IsAuthenticated]
    def get(self, request):
        serializer = UserProfileSerializer(request.user)
        return Response(serializer.data)
    def put(self, request):
        serializer = UserProfileSerializer(request.user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({'message': 'Profil mis à jour avec succès', 'user': serializer.data})
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class UserListView(APIView):
    """
    UserListView(APIView)
    ---------------------
    Vue d'API permettant à un agent ou superutilisateur de lister les utilisateurs.

    GET:
        Retourne la liste des utilisateurs, filtrable par rôle.
        - Permissions : Seuls les agents ou superutilisateurs peuvent accéder à cette vue.
        - Paramètres de requête : ?role=ROLE
        - Réponses :
            - 200 : Liste des utilisateurs.
            - 403 : Permission refusée.
    """
    permission_classes = [permissions.IsAuthenticated]
    def get(self, request):
        if not (request.user.is_agent or request.user.is_superuser_role):
            return Response({'error': 'Permission refusée'}, status=status.HTTP_403_FORBIDDEN)
        role_filter = request.query_params.get('role')
        queryset = User.objects.all()
        if role_filter:
            queryset = queryset.filter(role=role_filter)
        if request.user.is_agent:
            queryset = queryset.filter(role=User.UserRoles.CLIENT)
        serializer = UserListSerializer(queryset, many=True)
        return Response(serializer.data)

class UserValidationView(APIView):
    """
    UserValidationView(APIView)
    ---------------------------
    Vue d'API permettant à un agent ou un superutilisateur de valider ou rejeter un compte utilisateur de type client.

    POST:
        Valide ou rejette un compte client en fonction de la donnée 'is_active' fournie.
        - Permissions : Seuls les agents ou superutilisateurs peuvent accéder à cette vue.
        - Paramètres :
            - user_id (int) : Identifiant de l'utilisateur à valider ou rejeter.
            - Corps de la requête : { "is_active": bool }
        - Réponses :
            - 200 : Compte validé ou rejeté avec succès, retourne les informations de l'utilisateur.
            - 400 : Erreur de validation ou l'utilisateur n'est pas un client.
            - 403 : Permission refusée si l'utilisateur authentifié n'est ni agent ni superutilisateur.
    """
    permission_classes = [permissions.IsAuthenticated]
    def post(self, request, user_id):
        if not (request.user.is_agent or request.user.is_superuser_role):
            return Response({'error': 'Permission refusée'}, status=status.HTTP_403_FORBIDDEN)
        user = get_object_or_404(User, id=user_id)
        if user.role != User.UserRoles.CLIENT:
            return Response({'error': 'Seuls les comptes clients peuvent être validés'}, status=status.HTTP_400_BAD_REQUEST)
        serializer = UserValidationSerializer(data=request.data)
        if serializer.is_valid():
            user.is_active = serializer.validated_data['is_active']
            user.save()
            action = "validé" if user.is_active else "rejeté"
            return Response({'message': f'Compte {action} avec succès', 'user': UserListSerializer(user).data})
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class PendingUsersView(APIView):
    """
    PendingUsersView(APIView)
    -------------------------
    Vue d'API permettant à un agent ou superutilisateur de lister les comptes clients en attente de validation.

    GET:
        Retourne la liste des clients dont le compte n'est pas encore activé.
        - Permissions : Seuls les agents ou superutilisateurs peuvent accéder à cette vue.
        - Réponses :
            - 200 : Liste des utilisateurs en attente et leur nombre.
            - 403 : Permission refusée.
    """
    permission_classes = [permissions.IsAuthenticated]
    def get(self, request):
        if not (request.user.is_agent or request.user.is_superuser_role):
            return Response({'error': 'Permission refusée'}, status=status.HTTP_403_FORBIDDEN)
        pending_users = User.objects.filter(role=User.UserRoles.CLIENT, is_active=False)
        serializer = UserListSerializer(pending_users, many=True)
        return Response({'count': pending_users.count(), 'users': serializer.data})

@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def logout_view(request):
    """
    logout_view(request)
    -------------------
    Vue d'API permettant à un utilisateur authentifié de se déconnecter.

    POST:
        Déconnecte l'utilisateur courant.
        - Permissions : Authentification requise.
        - Réponses :
            - 200 : Déconnexion réussie.
    """
    logout(request)
    return Response({'message': 'Déconnexion réussie'})



##############################################################################################
# Création d'un agent par un superutilisateur
##############################################################################################


class IsSuperUserRole(permissions.BasePermission):
    def has_permission(self, request):
        return request.user.is_authenticated and request.user.is_superuser_role

class AgentCreateView(APIView):
    permission_classes = [permissions.IsAuthenticated, IsSuperUserRole]

    def post(self, request):
        data = request.data.copy()
        data['role'] = User.UserRoles.AGENT  # forcer le rôle à AGENT
        serializer = RegisterSerializer(data=data, context={'request': request})
        if serializer.is_valid():
            user = serializer.save()
            return Response({
                'message': 'Agent créé avec succès',
                'user': {
                    'id': user.id,
                    'username': user.username,
                    'email': user.email,
                    'role': user.role,
                    'is_active': user.is_active
                }
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)