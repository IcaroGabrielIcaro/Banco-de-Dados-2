from django.db import models
from django.contrib.auth.models import AbstractUser

class Usuario(AbstractUser):
    TIPO_PERFIL_CHOICES = [
        ('gerente', 'Gerente'),
        ('mecanico', 'Mecânico'),
        ('cliente', 'Cliente'),
    ]

    email = models.EmailField(unique=True)
    cpf = models.CharField(max_length=14, unique=True)
    telefone = models.CharField(max_length=20, blank=True, null=True)
    tipo_perfil = models.CharField(max_length=20, choices=TIPO_PERFIL_CHOICES)
    data_cadastro = models.DateTimeField(auto_now_add=True)
    ativo = models.BooleanField(default=True)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username", "cpf"]

    def __str__(self):
        return self.email
