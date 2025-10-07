from django.db import models


class Autor(models.Model):
    nome = models.CharField(max_length=100)
    data_nascimento = models.DateField()
    nacionalidade = models.CharField(max_length=100)

    def __str__(self):
        return self.nome


class Categoria(models.Model):
    nome = models.CharField(max_length=100)
    descricao = models.TextField(blank=True)

    def __str__(self):
        return self.nome


class Editora(models.Model):
    nome = models.CharField(max_length=100)
    endereco = models.TextField()

    def __str__(self):
        return self.nome


class Livro(models.Model):
    titulo = models.CharField(max_length=100)
    autor = models.ForeignKey(Autor, on_delete=models.CASCADE)
    ano_publicacao = models.IntegerField()
    genero = models.CharField(max_length=100)
    categoria = models.ForeignKey(Categoria, on_delete=models.SET_NULL, null=True, blank=True)
    editora = models.ForeignKey(Editora, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return self.titulo


class Usuario(models.Model):
    nome = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    data_registro = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.nome


class Emprestimo(models.Model):
    livro = models.ForeignKey(Livro, on_delete=models.CASCADE)
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE)
    data_emprestimo = models.DateField()
    data_devolucao = models.DateField(null=True, blank=True)

    def __str__(self):
        return f"{self.livro.titulo} emprestado por {self.usuario.nome}"


class Reserva(models.Model):
    livro = models.ForeignKey(Livro, on_delete=models.CASCADE)
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE)
    data_reserva = models.DateField()

    def __str__(self):
        return f"{self.usuario.nome} reservou {self.livro.titulo}"


class Multa(models.Model):
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE)
    valor = models.DecimalField(max_digits=6, decimal_places=2)
    data_pagamento = models.DateField(null=True, blank=True)

    def __str__(self):
        return f"Multa de R${self.valor} para {self.usuario.nome}"
