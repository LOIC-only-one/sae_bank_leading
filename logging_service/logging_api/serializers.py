from rest_framework import serializers
from .models import Log

class LogCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Log
        fields = [
            'level', 'type_action', 'visibilite',
            'identifiant_utilisateur', 'source', 'message', 'service_name'
        ]

class LogSerializer(serializers.ModelSerializer):
    class Meta:
        model = Log
        fields = '__all__'
