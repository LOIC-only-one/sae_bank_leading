from django.db import models

class Log(models.Model):
    LEVEL_CHOICES = [
        ('INFO', 'Info'),
        ('WARNING', 'Warning'),
        ('ERROR', 'Error'),
    ]

    TYPE_CHOICES = [
        ('SYSTEME', 'Système'),
        ('OPERATION', 'Opération bancaire'),
        ('UTILISATEUR', 'Utilisateur'),
        ('COMPTE', 'Compte bancaire'),
        ('CONNEXION', 'Connexion'),
        ('DECONNEXION', 'Déconnexion'),
        ('CREATION_COMPTE', 'Création de compte'),
        ('VALIDATION_COMPTE', 'Validation de compte'),
        ('REJET_COMPTE', 'Rejet de compte'),
        ('VIREMENT', 'Virement'),
        ('DEPOT', 'Dépôt'),
        ('RETRAIT', 'Retrait'),
        ('ERREUR_SYSTEME', 'Erreur système'),
        ('MISE_A_JOUR_UTILISATEUR', 'Mise à jour utilisateur'),
    ]

    VISIBILITE_CHOICES = [
        ('MEMBRES', 'Membres'),
        ('AGENTS', 'Agents'),
    ]

    level = models.CharField(max_length=10, choices=LEVEL_CHOICES)
    type_action = models.CharField(max_length=30, choices=TYPE_CHOICES)
    visibilite = models.CharField(max_length=10, choices=VISIBILITE_CHOICES)
    identifiant_utilisateur = models.CharField(max_length=100, blank=True, null=True)
    source = models.CharField(max_length=100)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    service_name = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return f"[{self.created_at}] {self.level} - {self.type_action} - {self.message[:40]}"
