from django.db import models
from django.contrib.auth.models import AbstractUser

class MeuUsuario(AbstractUser):
    cpf = models.CharField(max_length=11)
    data_nascimento = models.DateField()
    idade = models.IntegerField()
    endereco = models.CharField(max_length=255)

    def __str__(self):
        return self.username, self.email, self.first_name, self.last_name, self.cpf