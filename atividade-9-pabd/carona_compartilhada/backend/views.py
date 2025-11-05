from rest_framework import viewsets, filters, generics
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework_simplejwt.views import TokenObtainPairView
from .models import Usuario, PerfilUsuario, Veiculo, Carona, Solicitacao, Avaliacao, Chat
from .serializers import (
    UsuarioSerializer, PerfilUsuarioSerializer, VeiculoSerializer,
    CaronaSerializer, SolicitacaoSerializer, AvaliacaoSerializer, ChatSerializer, UsuarioRegisterSerializer, UsuarioTokenObtainPairSerializer, LogoutSerializer
)
from .filters import CaronaFilter

class UsuarioRegisterView(generics.CreateAPIView):
    queryset = Usuario.objects.all()
    permission_classes = [AllowAny]
    serializer_class = UsuarioRegisterSerializer


class UsuarioTokenObtainPairView(TokenObtainPairView):
    serializer_class = UsuarioTokenObtainPairSerializer


class UsuarioViewSet(viewsets.ModelViewSet):
    queryset = Usuario.objects.all()
    serializer_class = UsuarioSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['username', 'email', 'first_name', 'last_name']


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


class PerfilUsuarioViewSet(viewsets.ModelViewSet):
    queryset = PerfilUsuario.objects.all()
    serializer_class = PerfilUsuarioSerializer
    permission_classes = [IsAuthenticated]


class VeiculoViewSet(viewsets.ModelViewSet):
    queryset = Veiculo.objects.all()
    serializer_class = VeiculoSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['motorista', 'ativo']
    search_fields = ['modelo', 'marca', 'placa']


class CaronaViewSet(viewsets.ModelViewSet):
    queryset = Carona.objects.all()
    serializer_class = CaronaSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['motorista', 'status', 'origem', 'destino']
    search_fields = ['origem', 'destino']
    ordering_fields = ['data_hora_saida', 'preco_por_pessoa']
    filterset_class = CaronaFilter
    
    @action(detail=False, methods=['get'])
    def disponiveis(self, request):
        """Retorna apenas caronas disponíveis"""
        caronas = self.queryset.filter(status='DISPONIVEL', vagas_disponiveis__gt=0)
        serializer = self.get_serializer(caronas, many=True)
        return Response(serializer.data)


class SolicitacaoViewSet(viewsets.ModelViewSet):
    queryset = Solicitacao.objects.all()
    serializer_class = SolicitacaoSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['carona', 'passageiro', 'status']
    
    @action(detail=True, methods=['post'])
    def aceitar(self, request, pk=None):
        """Aceitar uma solicitação"""
        solicitacao = self.get_object()
        solicitacao.status = 'ACEITA'
        solicitacao.save()
        return Response({'status': 'Solicitação aceita'})
    
    @action(detail=True, methods=['post'])
    def recusar(self, request, pk=None):
        """Recusar uma solicitação"""
        solicitacao = self.get_object()
        solicitacao.status = 'RECUSADA'
        solicitacao.save()
        return Response({'status': 'Solicitação recusada'})


class AvaliacaoViewSet(viewsets.ModelViewSet):
    queryset = Avaliacao.objects.all()
    serializer_class = AvaliacaoSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['carona', 'avaliador', 'avaliado', 'tipo']


class ChatViewSet(viewsets.ModelViewSet):
    queryset = Chat.objects.all()
    serializer_class = ChatSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['carona', 'usuario']