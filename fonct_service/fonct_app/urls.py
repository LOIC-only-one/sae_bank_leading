from django.urls import path
from .views import lister_comptes_bancaires, creer_compte_bancaire, supprimer_compte, creer_operation, lister_operations_en_attente, valider_operation, rejeter_operation, lister_comptes_non_valides, valider_compte, supprimer_compte_admin, compte_rib

urlpatterns = [
    # Pour lister les comptes
    path('comptes/', lister_comptes_bancaires, name='lister_comptes_bancaires'),
    path('comptes/creer/', creer_compte_bancaire, name='creer_compte_bancaire'),
    path('comptes/supprimer/<int:compte_id>/', supprimer_compte, name='supprimer_compte'),
    path('comptes/modifier/<int:compte_id>/', supprimer_compte, name='modifier_compte'),
    path('comptes/rib/<str:rib>/', compte_rib, name='get_compte_by_rib'),


    path('comptes/non-valides/', lister_comptes_non_valides, name='comptes_non_valides'),
    path('comptes/valider/<int:compte_id>/', valider_compte, name='valider_compte'),
    path('comptes/admin-supprimer/<int:compte_id>/', supprimer_compte_admin, name='admin_supprimer_compte'),

    path('operations/creer/', creer_operation, name='creer_operation'),
    path('operations/en-attente/', lister_operations_en_attente, name='lister_operations'),
    path('operations/<int:operation_id>/valider/', valider_operation, name='valider_operation'),
    path('operations/<int:operation_id>/rejeter/', rejeter_operation, name='rejeter_operation'),
]