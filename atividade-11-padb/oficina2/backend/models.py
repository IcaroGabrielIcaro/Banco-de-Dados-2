from django.db import models
from autenticacao.models import Usuario

class Curso(models.Model):
    nome = models.CharField(max_length=100, unique=True)
    descricao = models.TextField()
    data_criacao = models.DateTimeField(auto_now_add=True)
    instrutor = models.ForeignKey(Usuario, on_delete=models.PROTECT, limit_choices_to={'perfilusuario__tipo_perfil': 'instrutor'})

    def __str__(self):
        return self.nome


class Modulo(models.Model):
    curso = models.ForeignKey(Curso, on_delete=models.CASCADE, related_name="modulos")
    titulo = models.CharField(max_length=100)
    ordem = models.PositiveIntegerField()

    class Meta:
        ordering = ['ordem']
        unique_together = ('curso', 'ordem')

    def __str__(self):
        return f"{self.curso.nome} - {self.titulo}"


class Aula(models.Model):
    modulo = models.ForeignKey(Modulo, on_delete=models.CASCADE, related_name="aulas")
    titulo = models.CharField(max_length=100)
    conteudo = models.TextField()
    duracao = models.PositiveIntegerField(help_text="Duração em minutos")
    ordem = models.PositiveIntegerField(default=1)

    class Meta:
        ordering = ['ordem']

    def __str__(self):
        return f"{self.modulo.titulo} - {self.titulo}"


class Matricula(models.Model):
    aluno = models.ForeignKey(
        Usuario,
        on_delete=models.CASCADE,
        limit_choices_to={'perfilusuario__tipo_perfil': 'aluno'}
    )
    curso = models.ForeignKey(Curso, on_delete=models.CASCADE)
    data_matricula = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('aluno', 'curso')

    def __str__(self):
        return f"{self.aluno.username} - {self.curso.nome}"
