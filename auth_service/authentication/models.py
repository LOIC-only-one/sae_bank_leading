from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    """
    Modèle utilisateur personnalisé étendant AbstractUser de Django pour supporter des champs et rôles supplémentaires.
    Attributs :
        role (str) : Rôle de l'utilisateur, parmi CLIENT, AGENT ou SUPER_USER.
        phone_number (str) : Numéro de téléphone optionnel de l'utilisateur.
        email (str) : Adresse email unique de l'utilisateur.
        address (str) : Adresse optionnelle de l'utilisateur.
        is_active (bool) : Indique si le compte utilisateur est actif. Par défaut à False.
        created_by_agent (User) : Référence à l'agent ayant créé cet utilisateur, si applicable.
        created_at (datetime) : Date de création de l'utilisateur.
        updated_at (datetime) : Date de dernière modification de l'utilisateur.
    Classes :
        UserRoles (TextChoices) : Enumération des rôles utilisateur (CLIENT, AGENT, SUPER_USER).
    Méthodes :
        __str__() : Retourne une représentation textuelle de l'utilisateur.
        save(*args, **kwargs) : Surcharge la sauvegarde pour définir le rôle et l'activation des superutilisateurs.
    Meta :
        db_table (str) : Nom personnalisé de la table 'auth_users'.
    """
    class UserRoles(models.TextChoices):
        CLIENT = 'CLIENT', 'Client'
        AGENT = 'AGENT', 'Agent'
        SUPER_USER = 'SUPER_USER', 'Super User'


    role = models.CharField(max_length=20, choices=UserRoles.choices, default=UserRoles.CLIENT)
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    email = models.EmailField(unique=True, blank=False, null=False)
    address = models.CharField(max_length=255, blank=True, null=True)

    is_active = models.BooleanField(default=False)
    created_by_agent = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, related_name='created_users')

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.username} ({self.role}) - {self.email}"

    def save(self, *args, **kwargs):
        if self.is_superuser:
            self.role = self.UserRoles.SUPER_USER
            self.is_active = True
        super().save(*args, **kwargs)
    
    class Meta:
        db_table = 'auth_users'
