from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authtoken.models import Token
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth import authenticate, login
from drf_yasg.utils import swagger_auto_schema

from .serializers import UsuarioSerializer, LoginSerializer


class RegistroUsuarioView(APIView):
    @swagger_auto_schema(
        request_body=UsuarioSerializer,
        responses={201: UsuarioSerializer}
    )
    def post(self, request):
        serializer = UsuarioSerializer(data=request.data)
        if serializer.is_valid():
            usuario = serializer.save()
            return Response(UsuarioSerializer(usuario).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



class LoginUsuarioView(ObtainAuthToken):
    serializer_class = LoginSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)

        email = serializer.validated_data['email']
        password = serializer.validated_data['password']

        usuario = authenticate(request, email=email, password=password)

        if usuario is None:
            return Response({'mensagem': 'Email ou senha inválidos.'},
                            status=status.HTTP_401_UNAUTHORIZED)

        login(request, usuario)
        
        token, created = Token.objects.get_or_create(user=usuario)
        if created:
            token.delete()
            token = Token.objects.create(user=usuario)

        usuario_serializado = UsuarioSerializer(usuario).data

        return Response({'token': token.key, 'usuario': usuario_serializado})


class LogoutUsuarioView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        token_key = request.auth.key
        try:
            token = Token.objects.get(key=token_key)
            token.delete()
        except Token.DoesNotExist:
            pass

        return Response({'detail': 'Usuário deslogado com sucesso.'}, status=status.HTTP_200_OK)


class PerfilUsuarioView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        usuario = request.user
        serializer = UsuarioSerializer(usuario)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @swagger_auto_schema(
        request_body=UsuarioSerializer,
        responses={201: UsuarioSerializer}
    )
    def put(self, request):
        usuario = request.user
        serializer = UsuarioSerializer(usuario, data=request.data, partial=True)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)