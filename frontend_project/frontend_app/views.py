from django.shortcuts import render, redirect
from django.contrib import messages
import requests
from django.views.decorators.http import require_http_methods
from datetime import datetime
from collections import Counter
from datetime import datetime, timedelta
from .utils import send_validation_email
import os
import re


AUTH_API_URL = os.getenv("AUTH_API_URL", "http://authservice:8000")
LOGGING_API_URL = os.getenv("LOGGING_API_URL", "http://loggingservice:8003")
API_BASE_URL_FONCT = "http://fonctservice:8002/api"



def token_required(view_func):
    """Décorateur pour vérifier si l'utilisateur est connecté via un token."""
    def wrapper(request, *args, **kwargs):
        if 'token' not in request.session:
            messages.error(request, "Vous devez être connecté pour accéder à cette page.")
            return redirect('login')
        return view_func(request, *args, **kwargs)
    return wrapper

def vitrine_view(request):
    return render(request, 'frontend_app/vitrine.html')



@token_required
def dashboard_view(request):
    headers = {'Authorization': f'Token {request.session.get("token")}'}
    user = request.session.get('user', {})
    liste_logs_transaction_historian = []

    comptes_response = requests.get(f"{API_BASE_URL_FONCT}/comptes/", headers=headers)
    if comptes_response.status_code == 200:
        comptes = comptes_response.json()
    else:
        comptes = []

    response = requests.get(f'{LOGGING_API_URL}/logs/', headers=headers)
    if response.status_code == 200:
        logs = response.json()

        OPERATION_TYPES = {
            'VIREMENT': 'Virement',
            'DEPOT': 'Dépôt',
            'RETRAIT': 'Retrait',
            'OPERATION': 'Opération bancaire',
            'TRANSFERT': 'Transfert',
        }

        for log in logs:
            type_action = log.get('type_action')
            user_id_log = str(log.get('identifiant_utilisateur'))
            current_user_id = str(user.get('id'))

            if user_id_log == current_user_id and type_action in OPERATION_TYPES:
                compte_id = log.get('compte_id')
                rib = None

                if compte_id is not None:
                    for compte in comptes:
                        if str(compte.get('id')) == str(compte_id):
                            rib = compte.get('numero_compte')
                            break

                if log.get('created_at'):
                    dt_obj = datetime.fromisoformat(log['created_at'].replace("Z", "+00:00"))
                    date_formatee = dt_obj.strftime("%d/%m/%Y %H:%M:%S")
                else:
                    date_formatee = ""

                montant = log.get('montant')
                if montant is None and log.get('message'):
                    match = re.search(r"([0-9]+(?:[.,][0-9]{1,2})?) ?€", log['message'])
                    if match:
                        montant = match.group(1).replace(',', '.')

                log_dict = {
                    'date': date_formatee,
                    'rib': rib,
                    'montant': montant,
                    'type_operation': OPERATION_TYPES.get(type_action, type_action),
                    'statut': log.get('level'),
                    'details': log.get('message')
                }
                liste_logs_transaction_historian.append(log_dict)

        def trier_par_date(log):
            return log['date']

        liste_logs_transaction_historian.sort(key=trier_par_date, reverse=True)
        # Ne garder que les 5 plus récentes
        liste_logs_transaction_historian = liste_logs_transaction_historian[:5]

    return render(request, 'frontend_app/home.html', {'user': user, 'historique': liste_logs_transaction_historian})

@token_required
def modifier_profil_view(request):
    headers = {'Authorization': f'Token {request.session.get("token")}'}
    profil_url = f"{AUTH_API_URL}/api/auth/profile/"
    reset_url = f"{AUTH_API_URL}/api/auth/password/reset/"

    response = requests.get(profil_url, headers=headers)
    if response.status_code != 200:
        messages.error(request, "Impossible de charger les données du profil.")
        return redirect('dashboard')

    user_data = response.json()

    if request.method == 'POST':
        old_password = request.POST.get("old_password")
        new_password = request.POST.get("new_password")
        confirm_password = request.POST.get("confirm_password")

        if old_password or new_password or confirm_password:
            if not all([old_password, new_password, confirm_password]):
                messages.error(request, "Pour changer le mot de passe, vous devez remplir les trois champs.")
                return redirect('profile')

            reset_data = {
                "old_password": old_password,
                "new_password": new_password,
                "confirm_password": confirm_password
            }
            reset_response = requests.post(reset_url, json=reset_data, headers=headers)

            if reset_response.status_code == 200:
                messages.success(request, "Mot de passe mis à jour avec succès.")
                send_validation_email(user_email=user_data.get('email'), message="Votre mot de passe a été changé avec succès.")
            else:
                erreurs = reset_response.json().get('error') or reset_response.text
                messages.error(request, f"Erreur lors du changement de mot de passe : {erreurs}")
                return redirect('profile')

        data = {
            'email': request.POST.get('email'),
            'username': request.POST.get('username'),
            'first_name': request.POST.get('first_name'),
            'last_name': request.POST.get('last_name'),
            'phone_number': request.POST.get('phone_number'),
            'address': request.POST.get('address'),
        }

        update_response = requests.put(profil_url, json=data, headers=headers)

        if update_response.status_code == 200:
            messages.success(request, "Profil mis à jour avec succès.")
            updated_user = requests.get(profil_url, headers=headers).json()
            request.session['user'] = updated_user
        else:
            messages.error(request, "Erreur lors de la mise à jour du profil.")

        return redirect('profile')

    return render(request, 'frontend_app/ALL/profile.html', {'user': user_data})

@token_required
def show_profile_view(request):
    headers = {'Authorization': f"Token {request.session.get('token')}"}
    response = requests.get(f"{AUTH_API_URL}/api/auth/profile/", headers=headers)
    if response.status_code == 200:
        user_data = response.json(); request.session['user'] = user_data
        return render(request, 'frontend_app/ALL/profile.html', {'user': user_data})
    else:
        messages.error(request, "Erreur lors de la récupération de votre profil.")
        return redirect('dashboard')
    

# ----------- Authentification et Inscription -----------
def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        response = requests.post(f"{AUTH_API_URL}/api/auth/login/", json={
            'username': username,
            'password': password
        })

        if response.status_code == 200:
            response_data = response.json()
            request.session['token'] = response_data['token']
            request.session['user'] = response_data['user']
            return redirect('dashboard')
        else:
            messages.error(request, "Identifiants invalides.")

    return render(request, 'frontend_app/login.html')


def register_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        password = request.POST.get('password')
        password_confirm = request.POST.get('confirm_password')

        response = requests.post(f"{AUTH_API_URL}/api/auth/register/", json={
            'username': username,
            'email': email,
            'first_name': first_name,
            'last_name': last_name,
            'password': password,
            'confirm_password': password_confirm,
        })

        if response.status_code == 201:
            user_data = response.json().get('user', {})
            user_email = user_data.get('email', email)
            if user_email:
                send_validation_email(
                    user_email=user_email,
                    message="Votre inscription a bien été prise en compte. Un agent va valider votre compte prochainement."
                )
            return redirect('login')
        else:
            error_data = response.json()
            error_message = error_data.get('detail') or error_data
            messages.error(request, f"Erreur lors de l'inscription: {error_message}")

    return render(request, 'frontend_app/register.html')

def logout_view(request):
    request.session.flush()
    return redirect('login')


# ----------- Gestion des Agents par les Super Utilisateurs -----------
@token_required
def create_agent_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        phone_number = request.POST.get('phone_number')
        address = request.POST.get('address')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')
        headers = {'Authorization': f"Token {request.session.get('token')}"}
        data = {'username': username, 'email': email, 'first_name': first_name, 'last_name': last_name, 'phone_number': phone_number, 'address': address, 'password': password, 'confirm_password': confirm_password, 'role': 'AGENT'}

        response = requests.post(f"{AUTH_API_URL}/api/auth/agents/create/", json=data, headers=headers)

        if response.status_code == 201:
            return redirect('dashboard')
        else:
            errors = response.json()
            messages.error(request, f"Erreur: {errors}")
            print(f"Erreur lors de la création de l'agent: {response.status_code} - {errors}")

        return render(request, 'frontend_app/SUPER_USER/create_agent.html')
    else:
        return render(request, 'frontend_app/SUPER_USER/create_agent.html')



# ----------- Gestion des Clients en Attente (Agents) -----------
@token_required
def pending_clients_view(request):
    headers = {'Authorization': f"Token {request.session.get('token')}"}

    response = requests.get(f"{AUTH_API_URL}/api/auth/users/pending/", headers=headers)

    if response.status_code == 200:
        data = response.json()
        pending_users = data.get('users', [])
        count = data.get('count', 0)

        return render(request, 'frontend_app/AGENT/liste_pending_users.html', {'pending_users': pending_users, 'count': count})
    else:
        messages.error(request, f"Erreur lors de la récupération des clients en attente. Code: {response.status_code}")
        return redirect('dashboard')

@token_required
def validate_user_view(request, user_id):
    user = request.session.get('user', {})
    if request.method == 'POST':
        headers = {'Authorization': f"Token {request.session.get('token')}"}

        response = requests.post(
            f"{AUTH_API_URL}/api/auth/users/{user_id}/validate/",
            headers=headers,
            json={'is_active': True}
        )

        if response.status_code == 200:
            user_data = response.json().get('user', {})
            user_email = user_data.get('email', None)
            if user_email:
                send_validation_email(
                    user_email=user_email,
                    message=f"Votre compte a été validé avec succès par {user.get('username', 'un agent')}. Vous pouvez maintenant vous connecter."
                )
        else:
            error_data = response.json()
            messages.error(request, f"Erreur lors de la validation: {error_data}")

    return redirect('pending_clients')

@token_required
def reject_user_view(request, user_id):
    user = request.session.get('user', {})
    if request.method == 'POST':
        headers = {'Authorization': f"Token {request.session.get('token')}"}
        response = requests.delete(f"{AUTH_API_URL}/api/auth/users/{user_id}/reject/", headers=headers)


        if response.status_code == 200:
            user_data = response.json().get('user', {})
            user_email = user_data.get('email', None)
            if user_email:
                send_validation_email(
                    user_email=user_email,
                    message=f"Votre compte a été rejeté par {user.get('username', 'un agent')}."
                )
        else:
            try:
                error_data = response.json()
            except Exception:
                error_data = response.text
            messages.error(request, f"Erreur lors du rejet: {error_data}")
    return redirect('pending_clients')


@token_required
def deactivate_user_view(request, user_id):
    user = request.session.get('user', {})
    if request.method == 'POST':
        headers = {'Authorization': f"Token {request.session.get('token')}"}
        response = requests.post(
            f"{AUTH_API_URL}/api/auth/users/{user_id}/validate/",
            headers=headers,
            json={'is_active': False}
        )

        if response.status_code == 200:
            user_data = response.json().get('user', {})
            user_email = user_data.get('email', None)
            if user_email:
                send_validation_email(
                    user_email=user_email,
                    message=f"Votre compte a été désactivé par {user.get('username', 'un agent')}."
                )
            messages.success(request, "Utilisateur désactivé avec succès.")
        else:
            messages.error(request, f"Erreur lors de la désactivation: {response.json()}")
    return redirect('pending_clients')

@token_required
def gerer_utilisateur_view(request):
    entetes = {'Authorization': f'Token {request.session.get("token")}'}
    utilisateur_connecte = request.session.get('user')

    if utilisateur_connecte.get("role") != "AGENT":
        messages.error(request, "Accès refusé.")
        return redirect("dashboard")

    reponse = requests.get(f"{AUTH_API_URL}/api/auth/users/?role=CLIENT", headers=entetes)
    if reponse.status_code == 200:
        utilisateurs = reponse.json().get("users", [])
    else:
        utilisateurs = []
        messages.error(request, "Impossible de récupérer la liste des utilisateurs.")

    return render(request, "frontend_app/AGENT/gerer_client.html", {
        "users": utilisateurs,
    })

@token_required
@require_http_methods(["POST"])
def gerer_utilisateur_action_view(request, utilisateur_id):
    entetes = {'Authorization': f'Token {request.session.get("token")}'}
    action = request.POST.get("action")

    reponse_compte = requests.get(f"{API_BASE_URL_FONCT}/comptes/user/{utilisateur_id}/", headers=entetes)
    a_comptes = reponse_compte.status_code == 200 and reponse_compte.json()
    
    if action == "disable":
        reponse = requests.post(
            f"{AUTH_API_URL}/api/auth/users/{utilisateur_id}/validate/",
            headers=entetes,
            json={'is_active': False}
        )
    elif action == "delete":
        if a_comptes:
            suppression_reussie = True
            for compte in a_comptes:
                compte_id = compte.get("id")
                del_response = requests.delete(f"{API_BASE_URL_FONCT}/comptes/admin-supprimer/{compte_id}/",headers=entetes)

                if del_response.status_code != 204:
                    suppression_reussie = False
                    messages.error(request, f"Échec de suppression du compte ID {compte_id}")
                    break

            if suppression_reussie:
                reponse = requests.delete(f"{AUTH_API_URL}/api/auth/users/{utilisateur_id}/reject/",headers=entetes)
                if reponse.status_code == 204:
                    messages.success(request, "Utilisateur et ses comptes ont été supprimés.")
                else:
                    messages.error(request, "Erreur lors de la suppression de l'utilisateur.")
        else:
            reponse = requests.delete(f"{AUTH_API_URL}/api/auth/users/{utilisateur_id}/reject/",headers=entetes)
            if reponse.status_code == 204:
                messages.success(request, "Utilisateur supprimé.")
            else:
                messages.error(request, "Erreur lors de la suppression.")

    elif action == "enable":
        reponse = requests.post(f"{AUTH_API_URL}/api/auth/users/{utilisateur_id}/validate/",headers=entetes,json={'is_active': True})
    
    return redirect('gerer_utilisateur')


# ----------- Gestion des Comptes (Membre) -----------
@token_required
def lister_comptes(request):
    token = request.session.get('token')
    if not token:
        messages.error(request, "Vous devez être connecté.")
        return redirect('login')
    
    headers = {'Authorization': f"Token {token}"}
    
    response = requests.get(f'{API_BASE_URL_FONCT}/comptes/', headers=headers)
    
    if response.status_code == 200:
        comptes = response.json()
        user = request.session.get('user', {})
    else:
        comptes = []
        error_msg = f'Erreur lors de la récupération des comptes. Status: {response.status_code}'
        messages.error(request, error_msg)

    nb_compte = 0
    for compte in comptes:
        if compte.get('est_valide', True):
            nb_compte += 1
        compte['date_creation_formatee'] = datetime.fromisoformat(compte['date_creation'].replace("Z", "")).strftime("%d/%m/%Y %H:%M")

    return render(request, 'frontend_app/MEMBER/lister_comptes.html', {'comptes': comptes, 'user': user, 'nb_compte': nb_compte})

@token_required
@require_http_methods(["GET", "POST"])
def creer_compte(request):
    if 'token' not in request.session:
        return redirect('login')
    
    token = request.session.get('token')
    
    if request.method == 'POST':
        numero_compte = request.POST.get('numero_compte')
        est_valide = request.POST.get('est_valide', False)
        
        if not numero_compte:
            return render(request, 'frontend_app/MEMBER/creer_compte.html')
        
        data = {"numero_compte": numero_compte,"est_valide": bool(est_valide)}
        
        headers = {'Authorization': f"Token {token}",'Content-Type': 'application/json'}
        
        response = requests.post(f"{API_BASE_URL_FONCT}/comptes/creer/", json=data, headers=headers)

        if response.status_code == 201:
            send_validation_email(user_email=request.session.get('user', {}).get('email'),message=f"Votre compte {numero_compte} a été créé avec succès. Un agent va le valider prochainement.")
            return redirect('lister_comptes')
        else:
            messages.error(request, "Erreur lors de la création du compte.")

    return render(request, 'frontend_app/MEMBER/creer_compte.html')


@token_required
@require_http_methods(["GET", "POST"])
def supprimer_compte(request, compte_id):
    token = request.session.get('token')
    headers = {'Authorization': f'Token {token}'}
    api_url = f'{API_BASE_URL_FONCT}/comptes/supprimer/{compte_id}/'
    response = requests.delete(api_url, headers=headers)
    
    if response.status_code == 204:
        messages.success(request, "Compte supprimé avec succès.")
    else:
        messages.error(request, f"Erreur lors de la suppression : {response.status_code}")
    return redirect('lister_comptes')

@token_required
@require_http_methods(["POST"])
def modifier_rib_view(request, compte_id):
    nouveau_rib = request.POST.get("nouveau_rib")
    if not nouveau_rib:
        messages.error(request, "Veuillez fournir un nouveau RIB.")
        return redirect('lister_comptes')

    user = request.session.get("user", {})
    headers = {'Authorization': f'Token {request.session.get("token")}'}
    data = {'numero_compte': nouveau_rib,'proprietaire_id': user.get('id')}

    response = requests.put(f"{API_BASE_URL_FONCT}/comptes/modifier/{compte_id}/", json=data, headers=headers)

    if response.status_code == 200:
        messages.success(request, "RIB mis à jour avec succès.")
    else:
        erreur = response.json()
        messages.error(request, f"Erreur lors de la mise à jour du RIB : {erreur}")

    return redirect('lister_comptes')


@token_required
@require_http_methods(["GET", "POST"])
def creer_operation_view(request, compte_id=None):
    headers = {'Authorization': f'Token {request.session.get("token")}'}
    type_from_url = None

    if 'depot' in request.path:
        type_from_url = 'depot'
    elif 'retrait' in request.path:
        type_from_url = 'retrait'
    elif 'virement' in request.path:
        type_from_url = 'virement'

    comptes_user = []
    r_comptes = requests.get(f'{API_BASE_URL_FONCT}/comptes/', headers=headers)
    if r_comptes.status_code == 200:
        comptes_user = r_comptes.json()

    if compte_id:
        found = False
        for compte in comptes_user:
            if compte["id"] == int(compte_id):
                found = True
                break
        if not found:
            messages.error(request, "Vous n'avez pas accès à ce compte.")
            return redirect('dashboard')

    if request.method == 'POST':
        rib_manuel = request.POST.get('rib_manuel')

        data = {
            'type_operation': request.POST.get('type_operation'),
            'montant': request.POST.get('montant'),
            'compte_de_credit': request.POST.get('compte_de_credit'),
            'compte_de_debit': request.POST.get('compte_de_debit')
        }

        if rib_manuel:
            rib_response = requests.get(f"{API_BASE_URL_FONCT}/comptes/rib/{rib_manuel}/", headers=headers)
            if rib_response.status_code == 200:
                data['compte_de_credit'] = rib_response.json().get("id")
            else:
                messages.error(request, "RIB externe invalide ou non trouvé.")
                return redirect(request.path)

        if type_from_url == 'depot':
            data['compte_de_credit'] = compte_id
        elif type_from_url == 'retrait':
            data['compte_de_debit'] = compte_id
        elif type_from_url == 'virement':
            data['compte_de_debit'] = compte_id

        response = requests.post(f"{API_BASE_URL_FONCT}/operations/creer/", json=data, headers=headers)
        if response.status_code == 201:
            messages.success(request, "Opération enregistrée avec succès.")
            return redirect('lister_comptes')
        else:
            messages.error(request, f"Erreur: {response.text}")

    return render(request, 'frontend_app/MEMBER/create_operation.html', {'type_operation': type_from_url,'compte_id': compte_id,'comptes_user': comptes_user})


# ----------- Gestion des Opérations en Attente (Agents) -----------

@token_required
def lister_operations_en_attente(request):
    utilisateur_connecte = request.session.get('user', {})
    jeton = request.session.get('token')
    entetes = {'Authorization': f'Token {jeton}'}

    reponse = requests.get(f"{API_BASE_URL_FONCT}/operations/en-attente/", headers=entetes)
    if reponse.status_code != 200:
        messages.error(request, "Erreur lors de la récupération des opérations en attente.")
        return redirect('dashboard')

    operations_en_attente = reponse.json()

    ids_utilisateurs = list({operation.get('effectue_par_id') for operation in operations_en_attente if operation.get('effectue_par_id')})

    infos_utilisateurs = {}
    for identifiant in ids_utilisateurs:
        reponse_utilisateur = requests.get(f"{AUTH_API_URL}/api/auth/users/{identifiant}/", headers=entetes)
        if reponse_utilisateur.status_code == 200:
            infos_utilisateurs[identifiant] = reponse_utilisateur.json()

    for operation in operations_en_attente:
        identifiant = operation.get('effectue_par_id')
        operation['effectue_par'] = infos_utilisateurs.get(identifiant)

    return render(request, 'frontend_app/AGENT/operations_pending.html', {
        'operations': operations_en_attente,
        'user': utilisateur_connecte,
    })


@token_required
def valider_operation_view(request, operation_id):
    if request.method == 'POST':
        headers = {'Authorization': f'Token {request.session["token"]}'}
        response = requests.post(f"{API_BASE_URL_FONCT}/operations/{operation_id}/valider/", headers=headers)
        if response.status_code == 200:
            messages.success(request, "Opération validée.")
        else:
            messages.error(request, f"Erreur : {response.text}")
    return redirect('lister_operations')

@token_required
def rejeter_operation_view(request, operation_id):
    if request.method == 'POST':
        headers = {'Authorization': f'Token {request.session["token"]}'}
        response = requests.post(f"{API_BASE_URL_FONCT}/operations/{operation_id}/rejeter/", headers=headers)
        if response.status_code == 200:
            messages.success(request, "Opération rejetée.")
        else:
            messages.error(request, f"Erreur : {response.text}")
    return redirect('lister_operations')

@token_required
def comptes_en_attente_view(request):
    """Afficher la liste des comptes à valider (agent)"""
    headers = {'Authorization': f'Token {request.session["token"]}'}
    response = requests.get(f"{API_BASE_URL_FONCT}/comptes/non-valides/", headers=headers)
    
    if response.status_code == 200:
        comptes = response.json()
        return render(request, 'frontend_app/AGENT/lister_comptes_non_valides.html', {'comptes': comptes})
    else:
        messages.error(request, "Erreur lors de la récupération des comptes.")
        return redirect('dashboard')



@token_required
def valider_compte_view(request, compte_id):
    """Valide un compte (agent uniquement)"""
    if request.method == 'POST':
        headers = {'Authorization': f'Token {request.session["token"]}'}
        response = requests.post(f"{API_BASE_URL_FONCT}/comptes/valider/{compte_id}/", headers=headers)
    return redirect('comptes_en_attente')


# ----------- Gestion des Logs (Agents + Membres) -----------
@token_required
def afficher_logs_view(request):
    utilisateur = request.session.get('user')
    if not utilisateur:
        return redirect('login')

    est_agent = utilisateur.get('role') == 'AGENT'
    url_base = "http://loggingservice:8003/logs/"
    entetes = {
        'Authorization': f"Token {request.session.get('token')}"
    }
    if est_agent:
        parametres = request.GET.dict()
    else:
        parametres = {'identifiant_utilisateur': utilisateur.get('id')}

    liste_logs = []
    reponse = requests.get(url_base, params=parametres, headers=entetes)
    if reponse.status_code == 200:
        liste_logs = reponse.json()
        for log in liste_logs:
            cree_le = log.get('created_at')
            if cree_le:
                dt = datetime.fromisoformat(cree_le.replace("Z", "+00:00"))
                log['created_at_formatted'] = dt.strftime("%d/%m/%Y %H:%M:%S")
    else:
        messages.error(request, f"Erreur récupération logs : {reponse.status_code}")

    # Statistiques pour agents uniquement
    statistiques = {}
    if est_agent:
        statistiques['total_events'] = len(liste_logs)

        # Erreurs critiques
        nb_erreurs = 0
        for log in liste_logs:
            if log.get('level') in ('ERROR'):
                nb_erreurs += 1
        statistiques['error_count'] = nb_erreurs

        # Actions par type
        compteur_type_action = Counter()
        for log in liste_logs:
            type_action = log.get('type_action')
            if type_action:
                compteur_type_action[type_action] += 1
        statistiques['actions_by_type'] = dict(compteur_type_action)

        # Visibilité
        compteur_visibilite = Counter()
        for log in liste_logs:
            visibilite = log.get('visibilite')
            if visibilite:
                compteur_visibilite[visibilite] += 1
        statistiques['visibilite_distribution'] = dict(compteur_visibilite)

        # Utilisateurs actifs (dernières 24h)
        maintenant = datetime.now(datetime.utcnow().astimezone().tzinfo)
        dernieres_24h = maintenant - timedelta(hours=24)
        utilisateurs_actifs = set()
        for log in liste_logs:
            cree_le = log.get('created_at')
            if cree_le:
                dt = datetime.fromisoformat(cree_le.replace("Z", "+00:00"))
                if dt >= dernieres_24h:
                    utilisateurs_actifs.add(log.get('identifiant_utilisateur'))
        statistiques['active_users'] = len(utilisateurs_actifs)

        # Répartition par niveau
        compteur_niveau = Counter()
        for log in liste_logs:
            niveau = log.get('level')
            if niveau:
                compteur_niveau[niveau] += 1
        statistiques['level_distribution'] = dict(compteur_niveau)

        # Top utilisateurs actifs
        compteur_utilisateur = Counter()
        for log in liste_logs:
            utilisateur_id = log.get('identifiant_utilisateur')
            if utilisateur_id:
                compteur_utilisateur[utilisateur_id] += 1
        statistiques['top_users'] = compteur_utilisateur.most_common(3)

        # Taux de succès
        total = statistiques['total_events']
        if total > 0:
            nb_succes = 0
            for log in liste_logs:
                if log.get('level') not in ('ERROR'):
                    nb_succes += 1
            statistiques['success_rate'] = (nb_succes / total) * 100
        else:
            statistiques['success_rate'] = 0

    return render(request, 'frontend_app/ALL/logs.html', {
        'is_agent': est_agent,
        'user': utilisateur,
        'params': parametres,
        'analytics': statistiques if est_agent else {},
        'logs': liste_logs,
    })

# ----------- Gestion des Comptes Utilisateur (Agents) -----------

@token_required
def voir_comptes_utilisateur_view(request, utilisateur_id):
    headers = {'Authorization': f'Token {request.session.get("token")}'}
    user = request.session.get("user")

    if user.get("role") != "AGENT":
        messages.error(request, "Accès interdit.")
        return redirect("dashboard")

    response = requests.get(f"{API_BASE_URL_FONCT}/comptes/user/{utilisateur_id}/", headers=headers)

    if response.status_code == 200:
        comptes = response.json()
        for compte in comptes:
            compte['date_creation_formatee'] = datetime.fromisoformat(compte['date_creation'].replace("Z", "")).strftime("%d/%m/%Y %H:%M")
    else:
        comptes = []

    return render(request, "frontend_app/AGENT/voir_comptes_client.html", {
        "comptes": comptes,
        "utilisateur_id": utilisateur_id
    })
