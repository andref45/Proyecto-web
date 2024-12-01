from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone

class Usuario(AbstractUser):
    ROL_CHOICES = [
        (1, 'Administrador'),
        (2, 'Cliente'),
    ]
    
    email = models.EmailField(unique=True)
    rol_id = models.IntegerField(choices=ROL_CHOICES, default=2)
    fecha_creacion = models.DateTimeField(default=timezone.now)

    # Agregar related_name para resolver conflictos
    groups = models.ManyToManyField(
        'auth.Group',
        related_name='usuario_set',
        blank=True,
        help_text='The groups this user belongs to.',
        verbose_name='groups',
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        related_name='usuario_set',
        blank=True,
        help_text='Specific permissions for this user.',
        verbose_name='user permissions',
    )

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    def __str__(self):
        return self.email