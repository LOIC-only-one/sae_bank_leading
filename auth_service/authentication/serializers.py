from rest_framework import serializers
from django.contrib.auth import authenticate
from django.contrib.auth.password_validation import validate_password
from .models import User

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, validators=[validate_password])
    confirm_password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = [
            'username', 'email', 'first_name', 'last_name',
            'password', 'confirm_password', 'phone_number', 'address', 'role'
        ]
        extra_kwargs = {
            'email': {'required': True},
            'first_name': {'required': True},
            'last_name': {'required': True},
        }

    def validate(self, data):
        if data['password'] != data['confirm_password']:
            raise serializers.ValidationError("Les deux mots de passe sont différents.")
        return data

    def validate_role(self, role):
        req = self.context.get('request')
        if role == User.UserRoles.AGENT:
            if not (req and req.user.is_authenticated and req.user.is_superuser):
                raise serializers.ValidationError("Tu dois être super admin pour créer un agent.")
        if role == User.UserRoles.SUPER_USER:
            raise serializers.ValidationError("Impossible de créer un super utilisateur.")
        return role

    def create(self, data):
        data.pop('confirm_password')
        raw_password = data.pop('password')
        user = User.objects.create_user(password=raw_password, **data)
        if user.role != User.UserRoles.CLIENT:
            user.is_active = True
        user.save()
        return user


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        user = authenticate(username=data.get('username'), password=data.get('password'))
        if not user:
            raise serializers.ValidationError("Mauvais identifiants.")
        if not user.is_active:
            raise serializers.ValidationError("Ton compte est désactivé.")
        data['user'] = user
        return data


class UserProfileSerializer(serializers.ModelSerializer):
    role_display = serializers.CharField(source='get_role_display', read_only=True)

    class Meta:
        model = User
        fields = [
            'id', 'username', 'email', 'first_name', 'last_name',
            'phone_number', 'address', 'role', 'role_display', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'username', 'role', 'created_at', 'updated_at']
        

class UserListSerializer(serializers.ModelSerializer):
    role_display = serializers.CharField(source='get_role_display', read_only=True)

    class Meta:
        model = User
        fields = [
            'id', 'username', 'email', 'first_name', 'last_name',
            'role', 'role_display', 'is_active', 'created_at'
        ]


class UserValidationSerializer(serializers.Serializer):
    is_active = serializers.BooleanField()
    reason = serializers.CharField(required=False, allow_blank=True)


class UserDeleteSerializer(serializers.Serializer):
    user_id = serializers.IntegerField()

    def validate_user_id(self, user_id):
        if not User.objects.filter(id=user_id).exists():
            raise serializers.ValidationError("Aucun utilisateur avec cet ID.")
        return user_id
