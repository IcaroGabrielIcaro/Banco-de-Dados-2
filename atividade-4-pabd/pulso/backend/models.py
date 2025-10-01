from django.db import models

class Usuario (models.Model):
    matricula = models.CharField(max_length=14)
    senha = models.CharField(max_length=128)
    ativo = models.BooleanField(default=True)
    ultimo_login = models.DateField(auto_now=True)
    criado_em = models.DateField(auto_now_add=True)
    atualizado_em = models.DateField(auto_now=True)

    def __str__ (self):
        return self.matricula
    
class Instituicao (models.Model):
    nome = models.CharField(max_length=255)
    endereco = models.CharField(max_length=255)
    cnpj = models.CharField(max_length=18)
    exige_vinculo = models.BooleanField(default=False)
    email = models.CharField(max_length=254)
    telefone = models.CharField(max_length=20)
    usuario = models.ForeignKey('Usuario', on_delete=models.CASCADE, related_name='instituicoes')

    def __str__ (self):
        return self.nome