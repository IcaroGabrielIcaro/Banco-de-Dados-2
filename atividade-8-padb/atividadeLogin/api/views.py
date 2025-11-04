from rest_framework import viewsets, generics, status
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework.decorators import action
from django.utils import timezone

from .models import Usuario, Projeto, Tarefa
from .serializers import (
    UsuarioSerializer,
    UsuarioTokenObtainPairSerializer,
    UsuarioRegisterSerializer,
    ProjetoSerializer,
    TarefaSerializer,
    LogoutSerializer
)


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


class LogoutView(generics.GenericAPIView):
    serializer_class = LogoutSerializer
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        """
        Invalida o token de refresh (logout seguro).
        O access token expira naturalmente após o tempo configurado.
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({"detail": "Logout realizado com sucesso."}, status=status.HTTP_205_RESET_CONTENT)


class ProjetoViewSet(viewsets.ModelViewSet):
    serializer_class = ProjetoSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Projeto.objects.filter(usuario=self.request.user)

    def perform_create(self, serializer):
        serializer.save(usuario=self.request.user)


class TarefaViewSet(viewsets.ModelViewSet):
    serializer_class = TarefaSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        queryset = Tarefa.objects.filter(projeto__usuario=user)
        projeto_id = self.kwargs.get('projeto_id')
        if projeto_id:
            queryset = queryset.filter(projeto_id=projeto_id)
        return queryset

    def perform_create(self, serializer):
        projeto_id = self.kwargs.get('projeto_id') or self.request.data.get('projeto')
        projeto = get_object_or_404(Projeto, id=projeto_id, usuario=self.request.user)
        serializer.save(projeto=projeto)

    @action(detail=True, methods=['patch'], url_path='concluir')
    def concluir_tarefa(self, request, pk=None):
        tarefa = self.get_object()
        if tarefa.concluida:
            return Response({'detail': 'A tarefa já está concluída.'}, status=status.HTTP_400_BAD_REQUEST)

        tarefa.concluida = True
        tarefa.data_conclusao = timezone.now()
        tarefa.save()

        serializer = self.get_serializer(tarefa)
        return Response(serializer.data, status=status.HTTP_200_OK)