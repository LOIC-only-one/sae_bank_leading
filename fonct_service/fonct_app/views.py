# ==============================
#        IMPORTS & SETUP
# ==============================

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from datetime import datetime
from .models import CompteBancaire, OperationBancaire
from .serializers import ListerComptesBancairesSerializer, InteractWithCompteBancaireSerializer, AfficheCompteBancaireSerializer, OperationBancaireSerializer
from .logging import send_log

# ==============================
#      COMPTES BANCAIRES - CLIENT
# ==============================

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def lister_comptes_bancaires(request):
    """
    Liste les comptes bancaires de l'utilisateur connecté.
    """
    comptes = CompteBancaire.objects.filter(proprietaire_id=request.user.id)
    serializer = ListerComptesBancairesSerializer(comptes, many=True)
    return Response(serializer.data, status=200)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def creer_compte_bancaire(request):
    """
    Crée un compte bancaire pour l'utilisateur connecté.
    """
    data = request.data.copy()
    data['proprietaire_id'] = request.user.id

    if not data.get('numero_compte'):
        return Response({"numero_compte": ["Ce champ est obligatoire."]}, status=400)

    serializer = InteractWithCompteBancaireSerializer(data=data)
    if serializer.is_valid():
        compte = serializer.save()
        # Ajout du log
        send_log("log.membres.info", {
            "level": "INFO",
            "type_action": "CREATION_COMPTE",
            "visibilite": "MEMBRES",
            "identifiant_utilisateur": str(request.user.id),
            "source": "fonct_service",
            "message": f"Création du compte bancaire {compte.numero_compte} pour l'utilisateur {request.user.username}. Un agent doit encore activer ce compte."
        })
        output_serializer = AfficheCompteBancaireSerializer(compte)
        return Response(output_serializer.data, status=201)
    return Response(serializer.errors, status=400)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def compte_rib(request, rib):
    """
    Retourne les informations de base d'un compte bancaire via son RIB.
    """
    compte = CompteBancaire.objects.filter(numero_compte=rib, est_valide=True).first()
    if not compte:
        return Response({"error": "Compte introuvable ou non validé."}, status=404)
    
    return Response({
        "id": compte.id,
        "proprietaire_id": compte.proprietaire_id,
        "numero_compte": compte.numero_compte
    }, status=200)


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def supprimer_compte(request, compte_id):
    """
    Supprime un compte bancaire de l'utilisateur connecté.
    """
    compte = CompteBancaire.objects.filter(id=compte_id, proprietaire_id=request.user.id).first()
    if not compte:
        return Response({'error': 'Compte non trouvé'}, status=404)
    compte.delete()
    # Ajout du log
    send_log("log.membres.info", {
        "level": "INFO",
        "type_action": "COMPTE",
        "visibilite": "MEMBRES",
        "identifiant_utilisateur": str(request.user.id),
        "source": "fonct_service",
        "message": f"Suppression du compte bancaire {compte_id} par l'utilisateur {request.user.username}."
    })
    return Response({'message': 'Compte supprimé avec succès.'}, status=204)

# ==============================
#      FONCTIONS MÉTIER
# ==============================

def virement_compte_bancaire(source_compte, destination_compte, montant):
    if source_compte.est_valide and destination_compte.est_valide:
        if source_compte.solde >= montant:
            source_compte.solde -= montant
            destination_compte.solde += montant
            source_compte.save()
            destination_compte.save()
            # Log virement
            send_log("log.membres.info", {
                "level": "INFO",
                "type_action": "VIREMENT",
                "visibilite": "AGENTS",
                "identifiant_utilisateur": str(source_compte.proprietaire_id),
                "source": "fonct_service",
                "message": f"Virement de {montant}€ du compte {source_compte.numero_compte} vers {destination_compte.numero_compte}."
            })
        else:
            send_log("log.membres.info", {
                "level": "ERROR",
                "type_action": "VIREMENT",
                "visibilite": "AGENTS",
                "identifiant_utilisateur": str(source_compte.proprietaire_id),
                "source": "fonct_service",
                "message": f"Échec du virement : solde insuffisant sur le compte {source_compte.numero_compte}."
            })
            raise ValueError("Solde insuffisant pour le virement.")
    else:
        send_log("log.membres.info", {
            "level": "ERROR",
            "type_action": "VIREMENT",
            "visibilite": "AGENTS",
            "identifiant_utilisateur": str(source_compte.proprietaire_id),
            "source": "fonct_service",
            "message": f"Échec du virement : un des comptes n'est pas valide ({source_compte.numero_compte}, {destination_compte.numero_compte})."
        })
        raise ValueError("Un des comptes n'est pas valide.")


def retrait_compte_bancaire(compte, montant):
    if compte.est_valide:
        if compte.solde >= montant:
            compte.solde -= montant
            compte.save()
            # Log retrait
            send_log("log.membres.info", {
                "level": "INFO",
                "type_action": "RETRAIT",
                "visibilite": "AGENTS",
                "identifiant_utilisateur": str(compte.proprietaire_id),
                "source": "fonct_service",
                "message": f"Retrait de {montant}€ sur le compte {compte.numero_compte}."
            })
        else:
            send_log("log.membres.info", {
                "level": "ERROR",
                "type_action": "RETRAIT",
                "visibilite": "AGENTS",
                "identifiant_utilisateur": str(compte.proprietaire_id),
                "source": "fonct_service",
                "message": f"Échec du retrait : solde insuffisant sur le compte {compte.numero_compte}."
            })
            raise ValueError("Solde insuffisant pour le retrait.")
    else:
        send_log("log.membres.info", {
            "level": "ERROR",
            "type_action": "RETRAIT",
            "visibilite": "AGENTS",
            "identifiant_utilisateur": str(compte.proprietaire_id),
            "source": "fonct_service",
            "message": f"Échec du retrait : le compte {compte.numero_compte} n'est pas valide."
        })
        raise ValueError("Le compte n'est pas valide.")


def ajout_compte_bancaire(compte, montant):
    if compte.est_valide:
        compte.solde += montant
        compte.save()
        # Log dépôt
        send_log("log.membres.info", {
            "level": "INFO",
            "type_action": "DEPOT",
            "visibilite": "AGENTS",
            "identifiant_utilisateur": str(compte.proprietaire_id),
            "source": "fonct_service",
            "message": f"Dépôt de {montant}€ sur le compte {compte.numero_compte}."
        })
    else:
        send_log("log.membres.info", {
            "level": "ERROR",
            "type_action": "DEPOT",
            "visibilite": "AGENTS",
            "identifiant_utilisateur": str(compte.proprietaire_id),
            "source": "fonct_service",
            "message": f"Échec du dépôt : le compte {compte.numero_compte} n'est pas valide."
        })
        raise ValueError("Le compte n'est pas valide.")


# ==============================
#   OPÉRATIONS BANCAIRES - CLIENT
# ==============================

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def creer_operation(request):
    """
    Un client demande une opération (dépôt, retrait ou virement).
    """
    data = request.data.copy()
    data['effectue_par_id'] = request.user.id
    data['statut'] = 'en_attente'

    serializer = OperationBancaireSerializer(data=data)
    if serializer.is_valid():
        operation = serializer.save()
        if operation.type_operation == 'retrait':
            if operation.compte_de_debit.proprietaire_id != request.user.id:
                return Response({"error": "Vous n'êtes pas propriétaire du compte de retrait."}, status=403)

        elif operation.type_operation == 'virement':
            if operation.compte_de_debit.proprietaire_id != request.user.id:
                return Response({"error": "Vous n'êtes pas propriétaire du compte émetteur."}, status=403)

            if operation.compte_de_credit == operation.compte_de_debit:
                return Response({"error": "Vous ne pouvez pas faire un virement vers le même compte."}, status=400)

            
        send_log("log.membres.info", {
            "level": "INFO",
            "type_action": operation.type_operation.upper(),
            "visibilite": "MEMBRES",
            "identifiant_utilisateur": str(request.user.id),
            "source": "fonct_service",
            "message": f"Demande d'opération '{operation.type_operation}' de {operation.montant}€ par l'utilisateur {request.user.username} sur le compte {operation.compte_de_debit.numero_compte if operation.compte_de_debit else operation.compte_de_credit.numero_compte}."
        })
        return Response({"message": "Opération enregistrée en attente de validation"}, status=201)
    return Response(serializer.errors, status=400)


# ==============================
#   OPÉRATIONS BANCAIRES - AGENT
# ==============================

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def lister_operations_en_attente(request):
    """
    Liste des opérations en attente (agents uniquement).
    """
    if 'agent' not in getattr(request.user, 'roles', []):
        return Response({"error": "Accès interdit"}, status=403)

    operations = OperationBancaire.objects.filter(statut='en_attente')
    serializer = OperationBancaireSerializer(operations, many=True)
    return Response(serializer.data)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def valider_operation(request, operation_id):
    """
    Valide une opération bancaire (agents uniquement).
    """
    if 'agent' not in getattr(request.user, 'roles', []):
        return Response({"error": "Accès interdit"}, status=403)

    try:
        operation = OperationBancaire.objects.get(id=operation_id)
        if operation.statut != 'en_attente':
            return Response({"error": "L'opération a déjà été traitée."}, status=400)

        if operation.type_operation == 'depot':
            ajout_compte_bancaire(operation.compte_de_credit, operation.montant)
        elif operation.type_operation == 'retrait':
            retrait_compte_bancaire(operation.compte_de_debit, operation.montant)
        elif operation.type_operation == 'virement':
            virement_compte_bancaire(operation.compte_de_debit, operation.compte_de_credit, operation.montant)
        else:
            return Response({"error": "Type d'opération inconnu"}, status=400)

        operation.statut = 'validee'
        operation.agent_validateur_id = request.user.id
        operation.date_validation = datetime.now()
        operation.save()

        send_log("log.membres.info", {
            "level": "INFO",
            "type_action": operation.type_operation.upper(),
            "visibilite": "AGENTS",
            "identifiant_utilisateur": str(operation.effectue_par_id),
            "source": "fonct_service",
            "message": f"Opération '{operation.type_operation}' validée par l'agent {request.user.username} (id={request.user.id}) pour le compte {operation.compte_de_debit.numero_compte if operation.compte_de_debit else operation.compte_de_credit.numero_compte} d'un montant de {operation.montant}€."
        })

        return Response({"message": "Opération validée avec succès."}, status=200)

    except OperationBancaire.DoesNotExist:
        return Response({"error": "Opération introuvable"}, status=404)

    except ValueError as ve:

        send_log("log.membres.info", {
            "level": "ERROR",
            "type_action": operation.type_operation.upper() if 'operation' in locals() else "OPERATION",
            "visibilite": "AGENTS",
            "identifiant_utilisateur": str(operation.effectue_par_id) if 'operation' in locals() else "",
            "source": "fonct_service",
            "message": f"Erreur lors de la validation de l'opération : {str(ve)}"
        })
        return Response({"error": str(ve)}, status=400)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def rejeter_operation(request, operation_id):
    """
    Rejette une opération (agents uniquement).
    """
    if 'agent' not in getattr(request.user, 'roles', []):
        return Response({"error": "Accès interdit"}, status=403)

    try:
        operation = OperationBancaire.objects.get(id=operation_id)
        if operation.statut != 'en_attente':
            return Response({"error": "L'opération a déjà été traitée."}, status=400)

        operation.statut = 'rejete'
        operation.agent_validateur_id = request.user.id
        operation.date_validation = datetime.now()
        operation.save()

        # Ajout du log
        send_log("log.membres.info", {
            "level": "INFO",
            "type_action": "REJET_OPERATION",
            "visibilite": "AGENTS",
            "identifiant_utilisateur": str(operation.effectue_par_id),
            "source": "fonct_service",
            "message": f"Opération '{operation.type_operation}' rejetée par l'agent {request.user.username} (id={request.user.id}) pour le compte {operation.compte_de_debit.numero_compte if operation.compte_de_debit else operation.compte_de_credit.numero_compte} d'un montant de {operation.montant}€."
        })

        return Response({"message": "Opération rejetée avec succès."}, status=200)

    except OperationBancaire.DoesNotExist:
        return Response({"error": "Opération introuvable"}, status=404)


# ==============================
#     VALIDATION ADMIN - AGENT
# ==============================

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def lister_comptes_non_valides(request):
    """
    Liste les comptes non validés (agents uniquement).
    """
    if 'agent' not in getattr(request.user, 'roles', []):
        return Response({"error": "Accès interdit"}, status=403)

    try:
        comptes = CompteBancaire.objects.filter(est_valide=False)
        serializer = ListerComptesBancairesSerializer(comptes, many=True)
        return Response(serializer.data, status=200)

    except Exception as e:
        return Response({"error": "Erreur serveur lors de la récupération des comptes"}, status=500)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def valider_compte(request, compte_id):
    """
    Valide un compte bancaire (agents uniquement).
    """
    roles = getattr(request.user, 'roles', [])
    if 'agent' not in [r.lower() for r in roles]:
        return Response({"error": "Accès interdit : vous devez être agent."}, status=403)

    try:
        compte = CompteBancaire.objects.get(id=compte_id, est_valide=False)
        compte.est_valide = True
        compte.save()
        # Ajout du log
        send_log("log.membres.info", {
            "level": "INFO",
            "type_action": "VALIDATION_COMPTE",
            "visibilite": "AGENTS",
            "identifiant_utilisateur": str(compte.proprietaire_id),
            "source": "fonct_service",
            "message": f"Compte bancaire {compte.numero_compte} validé par l'agent {request.user.username} (id={request.user.id})."
        })
        return Response({"message": "Compte validé."}, status=200)
    except CompteBancaire.DoesNotExist:
        return Response({"error": "Compte introuvable ou déjà validé."}, status=404)


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def supprimer_compte_admin(request, compte_id):
    """
    Supprime n'importe quel compte bancaire (agents uniquement).
    """
    roles = getattr(request.user, 'roles', [])
    if 'agent' not in [r.lower() for r in roles]:
        return Response({"error": "Accès interdit."}, status=403)

    try:
        compte = CompteBancaire.objects.get(id=compte_id)
        compte.delete()
        # Ajout du log
        send_log("log.membres.info", {
            "level": "INFO",
            "type_action": "COMPTE",
            "visibilite": "AGENTS",
            "identifiant_utilisateur": str(compte.proprietaire_id),
            "source": "fonct_service",
            "message": f"Suppression du compte bancaire {compte_id} par l'agent {request.user.username} (id={request.user.id})."
        })
        return Response({"message": "Compte supprimé avec succès."}, status=204)
    except CompteBancaire.DoesNotExist:
        return Response({"error": "Compte introuvable."}, status=404)
