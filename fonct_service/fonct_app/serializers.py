# SERIALIZER CORRIGÉ

from rest_framework import serializers
from .models import CompteBancaire, OperationBancaire

class AfficheCompteBancaireSerializer(serializers.ModelSerializer):
    argent = serializers.SerializerMethodField()
    proprietaire_display = serializers.SerializerMethodField()
    
    class Meta:
        model = CompteBancaire
        fields = ['id','proprietaire_id','proprietaire_display','numero_compte','solde','argent','date_creation','est_valide',]
        read_only_fields = ['id', 'date_creation', 'solde']
    
    def get_argent(self, obj):
        return f"{obj.solde} €"
    
    def get_proprietaire_display(self, obj):
        return f"Propriétaire ID : {obj.proprietaire_id}"

class InteractWithCompteBancaireSerializer(serializers.ModelSerializer):
    class Meta:
        model = CompteBancaire
        fields = ['proprietaire_id', 'numero_compte', 'est_valide']
        read_only_fields = ['id', 'date_creation', 'solde']
    
    def validate_proprietaire_id(self, value):
        if not value:
            raise serializers.ValidationError("Le proprietaire_id est obligatoire.")
        return value
    
    def validate(self, data):
        if not data.get('proprietaire_id'):
            raise serializers.ValidationError({
                'proprietaire_id': ['This field is required.']
            })
        
        if not data.get('numero_compte'):
            raise serializers.ValidationError({
                'numero_compte': ['This field is required.']
            })
            
        return data

    def create(self, validated_data):
        return CompteBancaire.objects.create(**validated_data)
    
    def update(self, instance, validated_data):
        proprietaire_id = validated_data.get('proprietaire_id')
        if proprietaire_id is not None:
            instance.proprietaire_id = proprietaire_id

        nouveau_num = validated_data.get('numero_compte')
        if nouveau_num is not None and nouveau_num != instance.numero_compte:
            if CompteBancaire.objects.filter(numero_compte=nouveau_num).exclude(pk=instance.pk).exists():
                raise serializers.ValidationError({
                    "numero_compte": "Le numéro de compte existe déjà."
                })
            instance.numero_compte = nouveau_num

        est_valide = validated_data.get('est_valide')
        if est_valide is not None:
            instance.est_valide = est_valide

        instance.save()
        return instance

    def delete(self, instance):
        instance.delete()
        return None


class ListerComptesBancairesSerializer(serializers.ModelSerializer):
    """Permet à chaque utilisateur de lister ses comptes bancaires"""
    argent = serializers.SerializerMethodField()
    
    class Meta:
        model = CompteBancaire
        fields = ['id', 'proprietaire_id', 'numero_compte', 'solde', 'argent', 'date_creation', 'est_valide']
        read_only_fields = ['id', 'date_creation', 'solde']
    def get_argent(self, obj):
        return f"{obj.solde} €"
    
class OperationBancaireSerializer(serializers.ModelSerializer):
    class Meta:
        model = OperationBancaire
        fields = '__all__'
        read_only_fields = ['statut', 'date_creation', 'agent_validateur_id', 'date_validation']
