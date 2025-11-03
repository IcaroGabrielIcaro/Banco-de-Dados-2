from rest_framework import viewsets, status
from .models import Usuario, Projeto, Tarefa
from .serializers import UsuarioSerializer, UsuarioTokenObtainPairSerializer, UsuarioRegisterSerializer, ProjetoSerializer, TarefaSerializer
from rest_framework.decorators import authentication_classes, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import TokenAuthentication, SessionAuthentication
from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework.authtoken.models import Token
from django.contrib.auth import authenticate
from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework import generics
from django.shortcuts import get_object_or_404

class UsuarioRegisterView(generics.CreateAPIView):
    queryset = Usuario.objects.all()
    permission_classes = [AllowAny]
    serializer_class = UsuarioRegisterSerializer


class UsuarioTokenObtainPairView(TokenObtainPairView):
    serializer_class = UsuarioTokenObtainPairSerializer


class UsuarioViewSet(viewsets.ModelViewSet):
    queryset = Usuario.objects.all()
    serializer_class = UsuarioSerializer
    permission_classes = [IsAuthenticated]
    
class ProjetoViewSet(viewsets.ModelViewSet):
    queryset = Projeto.objects.all()
    serializer_class = ProjetoSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Projeto.objects.filter(usuario=self.request.user)

    def perform_create(self, serializer):
        serializer.save(usuario=self.request.user)

class TarefaViewSet(viewsets.ModelViewSet):
    queryset = Tarefa.objects.all()
    serializer_class = TarefaSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = Tarefa.objects.filter(projeto__usuario=self.request.user)
        projeto_id = self.request.query_params.get('projeto_id')
        if projeto_id:
            queryset = queryset.filter(projeto_id=projeto_id)
        return queryset

    def perform_create(self, serializer):
        projeto_id = self.request.data.get('projeto')
        projeto = get_object_or_404(Projeto, id=projeto_id, usuario=self.request.user)
        serializer.save(projeto=projeto)