from django.db import models
from django.contrib.auth.models import AbstractUser

class Usuario(AbstractUser):
    cpf = models.CharField(max_length=11, unique=True)
    telefone = models.CharField(max_length=15, blank=True, null=True)

    def __str__(self):
        return self.username
    

class PerfilUsuario(models.Model):

    TIPOS_PERFIL = [
        ('aluno', 'Aluno'),
        ('instrutor', 'Instrutor'),
        ('admin', 'Administrador'),
    ]

    usuario = models.OneToOneField(Usuario, on_delete=models.CASCADE)
    tipo_perfil = models.CharField(max_length=20, choices=TIPOS_PERFIL)

    def __str__(self):
        return f"{self.usuario.username} - {self.get_tipo_perfil_display()}"