from rest_framework import viewsets, status
from .models import Usuario, Projeto, Tarefa
from .serializers import UsuarioSerializer, ProjetoSerializer, TarefaSerializer
from rest_framework.decorators import authentication_classes, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import TokenAuthentication, SessionAuthentication
from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework.authtoken.models import Token
from django.contrib.auth import authenticate
from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.tokens import RefreshToken

class UsuarioViewSet(viewsets.ModelViewSet):
    queryset = Usuario.objects.all()
    serializer_class = UsuarioSerializer 

    @api_view(['POST'])
    @permission_classes([AllowAny])
    def signup(request):
        serializer = UsuarioSerializer(data=request.data)

        if serializer.is_valid():
            user = serializer.save()
            password = request.data.get('password')

            if not password:
                return Response({'detail': 'Senha é obrigatória.'}, status=status.HTTP_400_BAD_REQUEST)

            user.set_password(password)
            user.save()

            refresh = RefreshToken.for_user(user)

            return Response({
                'refresh': str(refresh),
                'access': str(refresh.access_token),
                'user': UsuarioSerializer(user).data
            }, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @api_view(['POST'])
    def login(request):
        username = request.data.get('username')
        password = request.data.get('password')

        if not username or not password:
            return Response({'detail': 'Username e senha são obrigatórios.'}, status=status.HTTP_400_BAD_REQUEST)

        user = authenticate(username=username, password=password)

        if user is None:
            return Response({'detail': 'Credenciais inválidas.'}, status=status.HTTP_401_UNAUTHORIZED)

        token, created = Token.objects.get_or_create(user=user)
        serializer = UsuarioSerializer(user)

        return Response({'token': token.key, 'user': serializer.data}, status=status.HTTP_200_OK)
    
    @api_view(['POST'])
    def signup(request):
        serializer = UsuarioSerializer(data=request.data)

        if serializer.is_valid():
            user = serializer.save()
            password = request.data.get('password')
            if password:
                user.set_password(password)
                user.save()

            token, created = Token.objects.get_or_create(user=user)

            user_data = UsuarioSerializer(user).data

            return Response(
                {'token': token.key, 'user': user_data},
                status=status.HTTP_201_CREATED
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @api_view(['GET'])
    @authentication_classes([TokenAuthentication, SessionAuthentication])
    @permission_classes([IsAuthenticated])
    def test_token(request):
        return Response({"message": f"Token válido! Usuário autenticado: {request.user.email}"}, status=status.HTTP_200_OK)
    
class ProjetoViewSet(viewsets.ModelViewSet):
    queryset = Projeto.objects.all()
    serializer_class = ProjetoSerializer

class TarefaViewSet(viewsets.ModelViewSet):
    queryset = Tarefa.objects.all()
    serializer_class = TarefaSerializer