from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from datetime import datetime
from .models import CompteBancaire, OperationBancaire
from .serializers import ListerComptesBancairesSerializer, InteractWithCompteBancaireSerializer, AfficheCompteBancaireSerializer, OperationBancaireSerializer
from .logging import send_log
from .decorator_perso import agent_required

# ------------ VUES POUR LA GESTION DES COMPTES BANCAIRES ------------

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def lister_comptes_bancaires(request):
    """
    Liste les comptes bancaires de l'utilisateur connecté.
    """
    comptes = CompteBancaire.objects.filter(proprietaire_id=request.user.id)
    serializer = ListerComptesBancairesSerializer(comptes, many=True)
    return Response(serializer.data, status=200)

@api_view(['GET'])
@agent_required
@permission_classes([IsAuthenticated])
def comptes_by_user(request, user_id):
    """
    Liste les comptes d'un utilisateur donné (réservé aux agents).
    """
    comptes = CompteBancaire.objects.filter(proprietaire_id=user_id)
    serializer = ListerComptesBancairesSerializer(comptes, many=True)
    return Response(serializer.data, status=200)



@api_view(['POST'])
@permission_classes([IsAuthenticated])
def creer_compte_bancaire(request):
    """
    Permet à un utilisateur de créer un compte bancaire.
    """
    data = request.data.copy()
    data['proprietaire_id'] = request.user.id

    if not data.get('numero_compte'):
        return Response({"numero_compte": ["Ce champ est obligatoire."]}, status=400)

    serializer = InteractWithCompteBancaireSerializer(data=data)
    if serializer.is_valid():
        compte = serializer.save()
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
    
    return Response({"id": compte.id,"proprietaire_id": compte.proprietaire_id,"numero_compte": compte.numero_compte}, status=200)


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

    send_log("log.membres.info", {
        "level": "INFO",
        "type_action": "COMPTE",
        "visibilite": "MEMBRES",
        "identifiant_utilisateur": str(request.user.id),
        "source": "fonct_service",
        "message": f"Suppression du compte bancaire {compte_id} par l'utilisateur {request.user.username}."
    })
    return Response({'message': 'Compte supprimé avec succès.'}, status=204)


# ------------------ Logique des opérations bancaires ------------------

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


# ----------------------- VUES POUR LES OPÉRATIONS BANCAIRES -----------------------

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


#------------------ VUES POUR LA VALIDATION DES OPÉRATIONS BANCAIRES (AGENTS)------------------

@api_view(['GET'])
@agent_required
@permission_classes([IsAuthenticated])
def lister_operations_en_attente(request):
    """
    Liste des opérations en attente (agents uniquement) avec numéro de compte et solde.
    """
    operations = OperationBancaire.objects.filter(statut='en_attente')
    serializer = OperationBancaireSerializer(operations, many=True)
    operations_data = serializer.data

    # Enrichir les données avec numéro de compte et solde
    for i, operation in enumerate(operations):
        if operation.compte_de_debit:
            compte = operation.compte_de_debit
        elif operation.compte_de_credit:
            compte = operation.compte_de_credit
        else:
            compte = None

        if compte:
            operations_data[i]['numero_compte'] = compte.numero_compte
            operations_data[i]['solde_compte'] = compte.solde
        else:
            operations_data[i]['numero_compte'] = None
            operations_data[i]['solde_compte'] = None

    return Response(operations_data, status=200)


@api_view(['POST'])
@agent_required
@permission_classes([IsAuthenticated])
def valider_operation(request, operation_id):
    """
    Valide une opération bancaire (agents uniquement).
    """
    operation = OperationBancaire.objects.filter(id=operation_id).first()
    if not operation:
        return Response({"error": "Opération introuvable"}, status=404)

    if operation.statut != 'en_attente':
        return Response({"error": "L'opération a déjà été traitée."}, status=400)

    try:
        if operation.type_operation == 'depot':
            ajout_compte_bancaire(operation.compte_de_credit, operation.montant)
        elif operation.type_operation == 'retrait':
            retrait_compte_bancaire(operation.compte_de_debit, operation.montant)
        elif operation.type_operation == 'virement':
            virement_compte_bancaire(operation.compte_de_debit, operation.compte_de_credit, operation.montant)
        else:
            return Response({"error": "Type d'opération inconnu"}, status=400)
    except ValueError as ve:
        send_log("log.membres.info", {
            "level": "ERROR",
            "type_action": operation.type_operation.upper(),
            "visibilite": "AGENTS",
            "identifiant_utilisateur": str(operation.effectue_par_id),
            "source": "fonct_service",
            "message": f"Erreur lors de la validation de l'opération : {str(ve)}"
        })
        return Response({"error": str(ve)}, status=400)

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


@api_view(['POST'])
@agent_required
@permission_classes([IsAuthenticated])
def rejeter_operation(request, operation_id):
    """
    Rejette une opération (agents uniquement).
    """
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


# ----------------- VUES POUR LA VALIDATION DES COMPTES BANCAIRES (AGENTS) -----------------

@api_view(['GET'])
@agent_required
@permission_classes([IsAuthenticated])
def lister_comptes_non_valides(request):
    """
    Liste les comptes non validés (agents uniquement).
    """
    try:
        comptes = CompteBancaire.objects.filter(est_valide=False)
        serializer = ListerComptesBancairesSerializer(comptes, many=True)
        return Response(serializer.data, status=200)

    except Exception as e:
        return Response({"error": "Erreur serveur lors de la récupération des comptes"}, status=500)


@api_view(['POST'])
@agent_required
@permission_classes([IsAuthenticated])
def valider_compte(request, compte_id):
    """
    Valide un compte bancaire (agents uniquement).
    """
    compte = CompteBancaire.objects.filter(id=compte_id, est_valide=False).first()
    if not compte:
        return Response({"error": "Compte introuvable ou déjà validé."}, status=404)
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


@api_view(['DELETE'])
@agent_required
@permission_classes([IsAuthenticated])
def supprimer_compte_admin(request, compte_id):
    """
    Supprime n'importe quel compte bancaire (agents uniquement).
    """
    compte = CompteBancaire.objects.filter(id=compte_id).first()
    if not compte:
        return Response({"error": "Compte introuvable."}, status=404)
    compte.delete()

    send_log("log.membres.info", {
        "level": "INFO",
        "type_action": "COMPTE",
        "visibilite": "AGENTS",
        "identifiant_utilisateur": str(compte.proprietaire_id),
        "source": "fonct_service",
        "message": f"Suppression du compte bancaire {compte_id} par l'agent {request.user.username} (id={request.user.id})."
    })
    return Response({"message": "Compte supprimé avec succès."}, status=204)


@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def modifier_compte(request, compte_id):
    compte = CompteBancaire.objects.filter(id=compte_id, proprietaire_id=request.user.id).first()
    if not compte:
        return Response({'error': 'Compte non trouvé'}, status=404)

    serializer = InteractWithCompteBancaireSerializer(compte, data=request.data, partial=True)

    if serializer.is_valid():
        compte_modifie = serializer.save()
        send_log("log.membres.info", {
            "level": "INFO",
            "type_action": "COMPTE",
            "visibilite": "AGENTS",
            "identifiant_utilisateur": str(compte.proprietaire_id),
            "source": "fonct_service",
            "message": f"Modification du compte bancaire {compte_id} par l'agent {request.user.username} (id={request.user.id})."
        })
        return Response(AfficheCompteBancaireSerializer(compte_modifie).data, status=200)
    else:
        send_log("log.membres.info", {
            "level": "ERROR",
            "type_action": "COMPTE",
            "visibilite": "AGENTS",
            "identifiant_utilisateur": str(compte.proprietaire_id),
            "source": "fonct_service",
            "message": f"Erreur de validation lors de la modification du compte bancaire {compte_id} par l'agent {request.user.username} (id={request.user.id}): {serializer.errors}"
        })
        return Response(serializer.errors, status=400)
