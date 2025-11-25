from .serializers import LoginSerializer, UsuarioSerializer
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth import authenticate, login 
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authtoken.models import Token
from drf_yasg.utils import swagger_auto_schema

from rest_framework.authtoken.models import Token

from rest_framework.permissions import IsAuthenticated


class RegistroUsuarioView(APIView):
    @swagger_auto_schema( # configuração do swagger para entender quais os campos esperados na requisição
        request_body=UsuarioSerializer,
    )
    def post(self, request):
        serializer = UsuarioSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



class LoginUsuarioView(ObtainAuthToken):
    serializer_class = LoginSerializer

    @swagger_auto_schema( # configuração do swagger para entender quais os campos esperados na requisição
        request_body=LoginSerializer,
    )
    def post(self, request, *args, **kwargs):
        email = request.data.get('email')
        password = request.data.get('password')

        usuario = authenticate(request, username=email, password=password)
        if usuario is not None:
            login(request, usuario)
            token, created = Token.objects.get_or_create(user=usuario)
            if created:
                token.delete()  
                token = Token.objects.create(user=usuario)
            return Response({'token': token.key, 'email': usuario.email, 'perfil': usuario.tipo_perfil})
        else:
            return Response({'mensagem': 'Login ou Senha Inválido'}, status=status.HTTP_401_UNAUTHORIZED)



class LogoutUsuarioView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        print(request.headers) 
        token_key = request.auth.key
        token = Token.objects.get(key=token_key)
        token.delete()

        return Response({'detail': 'Usuário deslogado com sucesso.'})