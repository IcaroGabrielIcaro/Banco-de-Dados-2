from django.shortcuts import render
from rest_framework import viewsets
from .models import Usuario, Instituicao
from .serializers import UsuarioSerializer, InstituicaoSerializer

class UsuarioViewSet(viewsets.ModelViewSet):
    queryset = Usuario.objects.all()
    serializer_class = UsuarioSerializer

class InstituicaoViewSet(viewsets.ModelViewSet):
    queryset = Instituicao.objects.all()
    serializer_class = InstituicaoSerializer