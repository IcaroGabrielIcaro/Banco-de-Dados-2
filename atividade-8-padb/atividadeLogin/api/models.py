from django.contrib.auth.models import AbstractUser
from django.db import models

class Usuario(AbstractUser):
    bio = models.TextField(blank=True, null=True)
    data_cadastro = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.username


class Projeto(models.Model):
    STATUS_CHOICES = [
        ('P', 'Planejamento'),
        ('E', 'Em Andamento'),
        ('C', 'Concluído'),
    ]

    nome = models.CharField(max_length=200)
    descricao = models.TextField(blank=True, null=True)
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name="projetos")
    data_criacao = models.DateTimeField(auto_now_add=True)
    data_atualizacao = models.DateTimeField(auto_now=True)
    status = models.CharField(max_length=1, choices=STATUS_CHOICES, default='P')

    def __str__(self):
        return f"{self.nome} ({self.get_status_display()})"


class Tarefa(models.Model):
    PRIORIDADE_CHOICES = [
        ('B', 'Baixa'),
        ('M', 'Média'),
        ('A', 'Alta'),
    ]

    titulo = models.CharField(max_length=200)
    descricao = models.TextField(blank=True, null=True)
    projeto = models.ForeignKey(Projeto, on_delete=models.CASCADE, related_name="tarefas")
    concluida = models.BooleanField(default=False)
    prioridade = models.CharField(max_length=1, choices=PRIORIDADE_CHOICES, default='M')
    data_criacao = models.DateTimeField(auto_now_add=True)
    data_conclusao = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.titulo} - {self.get_prioridade_display()} ({'Concluída' if self.concluida else 'Pendente'})"