from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    """Prmet de creer un user custom avec AbstractUser et de lui ajouter des champs supplémentaires"""
    class UserRoles(models.TextChoices):
        CLIENT = 'CLIENT', 'Client'
        AGENT = 'AGENT', 'Agent'
        SUPER_USER = 'SUPER_USER', 'Super User'
    
    role = models.CharField(max_length=20, choices=UserRoles.choices, default=UserRoles.CLIENT)
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    email = models.EmailField(unique=True, blank=False, null=False)
    address = models.CharField(max_length=255, blank=True, null=True)
    is_active = models.BooleanField(default=False)
    created_by_agent = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, related_name='created_users', limit_choices_to={'role': UserRoles.AGENT})
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.username} ({self.role}) - {self.email}"
    
    def save(self, *args, **kwargs):
        """Permet de créer un super utilisateur avec le rôle SUPER_USER et l'activer automatiquement."""
        if self.is_superuser:
            self.role = self.UserRoles.SUPER_USER
            self.is_active = True
        super().save(*args, **kwargs)

    class Meta:
        db_table = 'auth_users'