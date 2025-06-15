from django.db import models

class CompteBancaire(models.Model):
    proprietaire_id = models.IntegerField()
    numero_compte = models.CharField(max_length=34, unique=True)
    solde = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    date_creation = models.DateTimeField(auto_now_add=True)
    est_valide = models.BooleanField(default=False)

    def __str__(self):
        return f"Compte {self.numero_compte} - Propriétaire ID: {self.proprietaire_id}"


class OperationBancaire(models.Model):
    TYPES_OPERATION = [
        ('depot', 'Dépôt'),
        ('retrait', 'Retrait'),
        ('virement', 'Virement'),
    ]

    STATUTS = [
        ('en_attente', 'En attente'),
        ('validee', 'Validée'),
        ('rejete', 'Rejetée'),
    ]

    type_operation = models.CharField(max_length=10, choices=TYPES_OPERATION)
    montant = models.DecimalField(max_digits=12, decimal_places=2)
    compte_de_debit = models.ForeignKey(CompteBancaire, on_delete=models.CASCADE, related_name='operations_debit', null=True, blank=True)
    compte_de_credit = models.ForeignKey(CompteBancaire, on_delete=models.CASCADE, related_name='operations_credit', null=True, blank=True)
    effectue_par_id = models.IntegerField()
    statut = models.CharField(max_length=10, choices=STATUTS, default='en_attente')
    date_creation = models.DateTimeField(auto_now_add=True)

    agent_validateur_id = models.IntegerField(null=True, blank=True)
    date_validation = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.get_type_operation_display()} de {self.montant} € - Statut: {self.get_statut_display()}"

