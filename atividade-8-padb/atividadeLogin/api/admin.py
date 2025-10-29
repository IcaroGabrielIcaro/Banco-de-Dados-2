from django.contrib import admin
from .models import Usuario, Projeto, Tarefa

admin.site.register(Usuario)
admin.site.register(Projeto)
admin.site.register(Tarefa)
