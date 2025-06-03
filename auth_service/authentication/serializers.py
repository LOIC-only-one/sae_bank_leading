from rest_framework import serializers
from django.contrib.auth import authenticate
from django.contrib.auth.password_validation import validate_password
from .models import User

class RegisterSerializer(serializers.ModelSerializer):
    """
    RegisterSerializer permet de gérer l'inscription d'un nouvel utilisateur.

    Champs :
        - username : Nom d'utilisateur unique.
        - email : Adresse email de l'utilisateur (obligatoire).
        - first_name : Prénom de l'utilisateur (obligatoire).
        - last_name : Nom de famille de l'utilisateur (obligatoire).
        - password : Mot de passe de l'utilisateur (écriture seule, validé par validate_password).
        - password_confirm : Confirmation du mot de passe (écriture seule).
        - phone_number : Numéro de téléphone de l'utilisateur.
        - address : Adresse de l'utilisateur.
        - role : Rôle de l'utilisateur (Client, Agent, etc.).

    Méthodes :
        - validate(attribut) : Vérifie que les mots de passe correspondent.
        - validate_role(value) : Vérifie que seul un super utilisateur peut créer un agent et qu'il est impossible de créer un super utilisateur via ce serializer.
        - create(validated_data) : Crée un nouvel utilisateur avec les données validées, active automatiquement les comptes non clients.

    Remarques :
        - Le champ password n'est jamais retourné dans les réponses.
        - Les règles de validation assurent la sécurité et la cohérence des rôles lors de l'inscription.
    """
    password = serializers.CharField(write_only=True, validators=[validate_password])
    password_confirm = serializers.CharField(write_only=True)
    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name', 'password', 'password_confirm', 'phone_number', 'address', 'role']
        extra_kwargs = {'email': {'required': True}, 'first_name': {'required': True}, 'last_name': {'required': True}}



    def validate(self, attribut):
        """        Valide les données d'inscription."""
        if attribut['password'] != attribut['password_confirm']:
            raise serializers.ValidationError("Les mots de passe ne correspondent pas.")
        return attribut
    
    def validate_role(self, value):
        """        Valide le rôle de l'utilisateur lors de l'inscription."""
        request = self.context.get('request')
        if value == User.UserRoles.AGENT:
            if not (request and request.user.is_authenticated and request.user.is_superuser_role):
                raise serializers.ValidationError("Seul un super utilisateur peut créer un agent.")
        if value == User.UserRoles.SUPER_USER:
            raise serializers.ValidationError("Impossible de créer un super utilisateur.")
        return value
    
    def create(self, validated_data):
        """        Crée un nouvel utilisateur avec les données validées."""
        validated_data.pop('password_confirm')
        password = validated_data.pop('password')
        user = User.objects.create_user(password=password, **validated_data)
        if user.role != User.UserRoles.CLIENT:
            user.is_active = True
        user.save()
        return user

class LoginSerializer(serializers.Serializer):
    """
    Serializer pour gérer l'authentification lors de la connexion d'un utilisateur.

    Champs :
        username (CharField) : Le nom d'utilisateur de l'utilisateur qui tente de se connecter.
        password (CharField) : Le mot de passe de l'utilisateur (écriture seule).

    Méthodes :
        validate(attribut) :
            Authentifie l'utilisateur avec les identifiants fournis.
            Exceptions :
                ValidationError : Si les identifiants sont incorrects ou si le compte est inactif.
            Retourne :
                dict : Les données validées incluant l'instance de l'utilisateur authentifié.
    """
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)
    def validate(self, attribut):
        user = authenticate(username=attribut.get('username'), password=attribut.get('password'))
        if not user:
            raise serializers.ValidationError("Identifiants incorrects.")
        if not user.is_active:
            raise serializers.ValidationError("Compte désactivé.")
        attribut['user'] = user
        return attribut

class UserProfileSerializer(serializers.ModelSerializer):
    """
    Serializer pour le modèle User, fournissant des informations détaillées sur le profil utilisateur.

    Champs :
        - id (int, lecture seule) : Identifiant unique de l'utilisateur.
        - username (str, lecture seule) : Nom d'utilisateur.
        - email (str) : Adresse email.
        - first_name (str) : Prénom.
        - last_name (str) : Nom de famille.
        - phone_number (str) : Numéro de téléphone.
        - address (str) : Adresse.
        - role (int, lecture seule) : Identifiant du rôle.
        - role_display (str, lecture seule) : Représentation lisible du rôle.
        - created_at (datetime, lecture seule) : Date de création.
        - updated_at (datetime, lecture seule) : Date de dernière modification.

    Remarques :
        - Le champ 'role_display' utilise la méthode get_role_display du modèle pour afficher un rôle lisible.
        - Les champs en lecture seule ne peuvent pas être modifiés via ce serializer.
    """
    role_display = serializers.CharField(source='get_role_display', read_only=True)
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'phone_number', 'address', 'role', 'role_display', 'created_at', 'updated_at']
        read_only_fields = ['id', 'username', 'role', 'created_at', 'updated_at']

class UserListSerializer(serializers.ModelSerializer):
    """
    Serializer pour lister les informations des utilisateurs.

    Ce serializer fournit une représentation du modèle User, incluant les informations de base
    telles que le nom d'utilisateur, l'email, le prénom, le nom, le rôle et le statut du compte.
    Il inclut également une représentation lisible du rôle de l'utilisateur.

    Champs :
        - id : Identifiant unique de l'utilisateur.
        - username : Nom d'utilisateur.
        - email : Adresse email.
        - first_name : Prénom.
        - last_name : Nom de famille.
        - role : Rôle (tel qu'enregistré en base).
        - role_display : Représentation lisible du rôle.
        - is_active : Booléen indiquant si le compte est actif.
        - created_at : Date de création du compte.
    """
    role_display = serializers.CharField(source='get_role_display', read_only=True)
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'role', 'role_display', 'is_active', 'created_at']

class UserValidationSerializer(serializers.Serializer):
    """
    Serializer pour la validation de l'utilisateur (activation/désactivation).

    Champs :
        - is_active : Booléen indiquant si l'utilisateur est actif.
        - reason : Raison (optionnelle) pour la modification du statut.
    """
    is_active = serializers.BooleanField()
    reason = serializers.CharField(required=False, allow_blank=True)
