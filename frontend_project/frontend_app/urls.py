from django.urls import path
from .views import login_view, logout_view, vitrine_view, dashboard_view, register_view, create_agent_view, pending_clients_view, validate_user_view, reject_user_view, lister_comptes, creer_compte, supprimer_compte, creer_operation_view, comptes_en_attente_view, valider_compte_view, lister_operations_en_attente, valider_operation_view, rejeter_operation_view, afficher_logs_view, modifier_profil_view, gerer_utilisateur_view, gerer_utilisateur_action_view, modifier_rib_view, voir_comptes_utilisateur_view

urlpatterns = [

    #### Vitrine et dashboard (FAIT)
    path('', vitrine_view, name='vitrine'),
    path('dashboard/', dashboard_view, name='dashboard'), 

    #### Authentification et gestion des utilisateurs (FAIT)
    path('login/', login_view, name='login'),
    path('register/', register_view, name='register'),
    path('logout/', logout_view, name='logout'),

    #### Gestion des utilisateurs et agents et interacction avec API auth (FAIT)
    path('create/agent/', create_agent_view, name='create_agent'),
    path('client/pending/', pending_clients_view, name='pending_clients'), 
    path('client/validate/<int:user_id>/', validate_user_view, name='validate_user'),
    path('client/reject/<int:user_id>/', reject_user_view, name='reject_user'),
    path('client/profile/', modifier_profil_view, name='profile'),
    path('agent/gerer-utilisateurs/', gerer_utilisateur_view, name='gerer_utilisateur'),
    path('agent/gerer-utilisateur/<int:utilisateur_id>/', gerer_utilisateur_action_view, name='gerer_utilisateur_action'),
    path('agent/utilisateur/<int:utilisateur_id>/comptes/', voir_comptes_utilisateur_view, name='voir_comptes_utilisateur'),

    #### Gestion des comptes bancaires pour un utilisateur connecté (client) (FAIT)
    path('comptes/', lister_comptes, name='lister_comptes'),                                   
    path('comptes/creer/', creer_compte, name='creer_compte'),
    path('comptes/supprimer/<int:compte_id>/', supprimer_compte, name='supprimer_compte'),
    path('comptes/modifier/<int:compte_id>/', modifier_rib_view, name='modifier_rib'),
    path('comptes/<int:compte_id>/depot/', creer_operation_view, name='depot_operation'),
    path('comptes/<int:compte_id>/retrait/', creer_operation_view, name='retrait_operation'),
    path('comptes/<int:compte_id>/virement/', creer_operation_view, name='virement_operation'),

    ### Gestion des comptes bancaires pour les agents (FAIT)
    path('bank/pending/', creer_compte, name='pending_accounts'),
    path('bank/comptes-en-attente/', comptes_en_attente_view, name='comptes_en_attente'),
    path('bank/valider/<int:compte_id>/', valider_compte_view, name='valider_compte_frontend'),

    ### Validation des opérations bancaires par les agents
    path('operations/en-attente/', lister_operations_en_attente, name='lister_operations'),
    path('operations/creer/', creer_operation_view, name='creer_operation'),
    path('operations/valider/<int:operation_id>/', valider_operation_view, name='valider_operation'),
    path('operations/rejeter/<int:operation_id>/', rejeter_operation_view, name='rejeter_operation'),

    #### Affichage des logs (FAIT)
    path('logs/', afficher_logs_view, name='afficher_logs'),


]
