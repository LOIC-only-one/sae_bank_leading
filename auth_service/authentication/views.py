from rest_framework import status, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.views import APIView
from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from .serializers import RegisterSerializer, LoginSerializer, UserProfileSerializer, UserListSerializer, UserValidationSerializer
from rest_framework.authtoken.models import Token
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import TokenAuthentication
from .logging import send_log
from django.contrib.auth.password_validation import validate_password

Utilisateur = get_user_model()


class RegisterView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, requete):
        print("Données de la requête:", requete.data)
        serialiseur = RegisterSerializer(data=requete.data, context={'request': requete})
        if serialiseur.is_valid():
            new_utilisateur = serialiseur.save()

            # Ajout du log via send_log
            send_log("log.membres.info", {
                "level": "INFO",
                "type_action": "CREATION_COMPTE",
                "visibilite": "MEMBRES",
                "identifiant_utilisateur": str(new_utilisateur.id),
                "source": "auth_service",
                "message": f"Nouvel utilisateur créé: {new_utilisateur.username} mais en attente de validation par un agent."
            })

            return Response({
                'message': 'Compte créé',
                'user': {'id': new_utilisateur.id,'username': new_utilisateur.username,'email': new_utilisateur.email,'role': new_utilisateur.role,'is_active': new_utilisateur.is_active,'first_name': new_utilisateur.first_name,'last_name': new_utilisateur.last_name,'phone_number': new_utilisateur.phone_number,'address': new_utilisateur.address}
            }, status=status.HTTP_201_CREATED)
        return Response(serialiseur.errors, status=status.HTTP_400_BAD_REQUEST)


class LoginView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, requete):
        serialiseur = LoginSerializer(data=requete.data)
        if serialiseur.is_valid():
            utilisateur = serialiseur.validated_data['user']
            token, _ = Token.objects.get_or_create(user=utilisateur)

            send_log("log.membres.info", {
                "level": "INFO",
                "type_action": "CONNEXION",
                "visibilite": "MEMBRES",
                "identifiant_utilisateur": str(utilisateur.id),
                "source": "auth_service",
                "message": f"Utilisateur {utilisateur.username} connecté."
            })

            return Response({"token": token.key, "user": {"id": utilisateur.id, "username": utilisateur.username, "role": utilisateur.role, "email": utilisateur.email, "is_active": utilisateur.is_active, "first_name": utilisateur.first_name, "last_name": utilisateur.last_name, "phone_number": utilisateur.phone_number, "address": utilisateur.address}})
        return Response(serialiseur.errors, status=status.HTTP_400_BAD_REQUEST)

class ProfileView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def get(self, requete):
        serialiseur = UserProfileSerializer(requete.user)
        return Response(serialiseur.data)

    def put(self, requete):
        serialiseur = UserProfileSerializer(requete.user, data=requete.data, partial=True)
        if serialiseur.is_valid():
            serialiseur.save()

            send_log("log.membres.info", {
                "level": "INFO",
                "type_action": "MISE_A_JOUR_UTILISATEUR",
                "visibilite": "MEMBRES",
                "identifiant_utilisateur": str(requete.user.id),
                "source": "auth_service",
                "message": f"Profil mis à jour par {requete.user.username}."
            })

            return Response({'message': 'Profil mis à jour', 'user': serialiseur.data})
        return Response(serialiseur.errors, status=status.HTTP_400_BAD_REQUEST)

class UserDetailView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request, user_id):
        utilisateur = get_object_or_404(Utilisateur, id=user_id)
        serialiseur = UserListSerializer(utilisateur)
        return Response(serialiseur.data)

class UserListView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def get(self, requete):
        utilisateur = requete.user
        agent_verification = utilisateur.role == Utilisateur.UserRoles.AGENT
        super_verification = utilisateur.is_superuser or utilisateur.role == Utilisateur.UserRoles.SUPER_USER
        role = requete.query_params.get('role')
        utilisateurs = Utilisateur.objects.all()

        if not (agent_verification or super_verification):
            return Response({'error': 'Accès refusé'}, status=status.HTTP_403_FORBIDDEN)

        if role:
            utilisateurs = utilisateurs.filter(role=role)
        if agent_verification and not super_verification:
            utilisateurs = utilisateurs.filter(role=Utilisateur.UserRoles.CLIENT)

        serialiseur = UserListSerializer(utilisateurs, many=True)
        return Response({'count': utilisateurs.count(), 'users': serialiseur.data})


class UserValidationView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def post(self, requete, user_id):
        utilisateur_actuel = requete.user
        agent_verification = utilisateur_actuel.role == Utilisateur.UserRoles.AGENT
        super_verification = utilisateur_actuel.is_superuser or utilisateur_actuel.role == Utilisateur.UserRoles.SUPER_USER

        cible = get_object_or_404(Utilisateur, id=user_id)
        donnees = requete.data
        serialiseur = UserValidationSerializer(data=donnees)

        if not (agent_verification or super_verification):
            return Response({'error': 'Accès refusé'}, status=status.HTTP_403_FORBIDDEN)
        if cible.role != Utilisateur.UserRoles.CLIENT:
            return Response({'error': "Seuls les clients peuvent être validés."}, status=status.HTTP_400_BAD_REQUEST)
        if 'is_active' not in donnees:
            return Response({'error': 'Champ "is_active" manquant'}, status=status.HTTP_400_BAD_REQUEST)

        if serialiseur.is_valid():
            cible.is_active = serialiseur.validated_data['is_active']
            cible.save()

            send_log("log.membres.info", {
                "level": "INFO",
                "type_action": "VALIDATION_COMPTE" if cible.is_active else "REJET_COMPTE",
                "visibilite": "AGENTS",
                "identifiant_utilisateur": str(cible.id),
                "source": "auth_service",
                "message": f"Compte client {'validé' if cible.is_active else 'rejeté'} par {utilisateur_actuel.username}."
            })

            return Response({'message': 'Compte mis à jour', 'user': UserListSerializer(cible).data})
        return Response(serialiseur.errors, status=status.HTTP_400_BAD_REQUEST)


class PendingUsersView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def get(self, requete):
        utilisateur = requete.user
        agent_verification = utilisateur.role == Utilisateur.UserRoles.AGENT
        super_verification = utilisateur.is_superuser or utilisateur.role == Utilisateur.UserRoles.SUPER_USER
        if not (agent_verification or super_verification):
            return Response({'error': 'Accès refusé'}, status=status.HTTP_403_FORBIDDEN)

        utilisateurs = Utilisateur.objects.filter(role=Utilisateur.UserRoles.CLIENT, is_active=False)
        serialiseur = UserListSerializer(utilisateurs, many=True)
        return Response({'count': utilisateurs.count(), 'users': serialiseur.data})


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def logout_view(requete):
    entete_auth = requete.META.get('HTTP_AUTHORIZATION')
    if entete_auth and entete_auth.startswith('Token '):
        cle_token = entete_auth.split(' ')[1]
        try:
            token = Token.objects.get(key=cle_token)
            token.delete()
            return Response({'message': 'Déconnecté'})
        except Token.DoesNotExist:
            return Response({'message': 'Déjà déconnecté'})
    return Response({'message': 'Déjà déconnecté'})


class AgentCreateView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def post(self, requete):
        if not (requete.user.is_superuser or requete.user.role == Utilisateur.UserRoles.SUPER_USER):
            return Response({'error': 'Seuls les super users peuvent créer un agent'}, status=status.HTTP_403_FORBIDDEN)

        donnees = requete.data.copy()
        donnees['role'] = Utilisateur.UserRoles.AGENT
        donnees['is_active'] = True

        serialiseur = RegisterSerializer(data=donnees, context={'request': requete})
        if serialiseur.is_valid():
            nouvel_agent = serialiseur.save()
            token, _ = Token.objects.get_or_create(user=nouvel_agent)

            send_log("log.membres.info", {
                "level": "INFO",
                "type_action": "CREATION_COMPTE",
                "visibilite": "AGENTS",
                "identifiant_utilisateur": str(nouvel_agent.id),
                "source": "auth_service",
                "message": f"Nouvel agent créé: {nouvel_agent.username} par {requete.user.username}."
            })

            return Response({
                'message': 'Agent créé',
                'user': {'id': nouvel_agent.id,'username': nouvel_agent.username,'email': nouvel_agent.email,'role': nouvel_agent.role,'is_active': nouvel_agent.is_active,'token': token.key}
            }, status=status.HTTP_201_CREATED)
        return Response(serialiseur.errors, status=status.HTTP_400_BAD_REQUEST)

class UserDeleteView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def delete(self, requete, user_id):
        utilisateur = requete.user
        if not utilisateur.role == Utilisateur.UserRoles.AGENT or utilisateur.is_superuser or utilisateur.role == Utilisateur.UserRoles.SUPER_USER:
            return Response({'error': 'Accès refusé'}, status=status.HTTP_403_FORBIDDEN)
        

        cible = get_object_or_404(Utilisateur, id=user_id)
        cible.delete()
        send_log("log.membres.info", {
            "level": "INFO",
            "type_action": "SUPPRESSION_COMPTE",
            "visibilite": "AGENTS",
            "identifiant_utilisateur": str(cible.id),
            "source": "auth_service",
            "message": f"Utilisateur {cible.username} supprimé par {utilisateur.username}."
        })
        return Response({'message': 'Utilisateur supprimé'}, status=status.HTTP_204_NO_CONTENT)



class ResetPasswordView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        utilisateur = request.user
        ancien_mdp = request.data.get('old_password')
        nouveau_mdp = request.data.get('new_password')
        confirm_mdp = request.data.get('confirm_password')

        if not ancien_mdp or not nouveau_mdp or not confirm_mdp:
            return Response({'error': 'Les champs "old_password", "new_password" et "confirm_password" sont requis.'}, status=status.HTTP_400_BAD_REQUEST)

        if not utilisateur.check_password(ancien_mdp):
            return Response({'error': 'L’ancien mot de passe est incorrect.'}, status=status.HTTP_400_BAD_REQUEST)

        if nouveau_mdp != confirm_mdp:
            return Response({'error': 'Les nouveaux mots de passe ne correspondent pas.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            validate_password(nouveau_mdp, utilisateur)
        except Exception as erreur:
            return Response({'error': str(erreur)}, status=status.HTTP_400_BAD_REQUEST)

        utilisateur.set_password(nouveau_mdp)
        utilisateur.save()

        send_log("log.membres.info", {
            "level": "INFO",
            "type_action": "MISE_A_JOUR_UTILISATEUR",
            "visibilite": "MEMBRES",
            "identifiant_utilisateur": str(utilisateur.id),
            "source": "auth_service",
            "message": f"Mot de passe modifié par {utilisateur.username}."
        })

        return Response({'message': 'Mot de passe mis à jour avec succès.'}, status=status.HTTP_200_OK)
    

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def validate_token(requete):
    return Response({
        "valid": True,
        "user_id": requete.user.id,
        "username": requete.user.username,
        "role": getattr(requete.user, "role", None)
    })

