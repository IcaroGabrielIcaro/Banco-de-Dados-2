from rest_framework import status, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from .serializers import RegistroSerializer, UsuarioSerializer
from drf_yasg.utils import swagger_auto_schema
from rest_framework.views import APIView

# @api_view(['POST'])
# @permission_classes([permissions.AllowAny])
# @swagger_auto_schema(request_body=RegistroSerializer)
# def register_view(request):
#     serializer = RegistroSerializer(data=request.data)

#     if serializer.is_valid():
#         usuario = serializer.save()

#         refresh = RefreshToken.for_user(usuario)

#         return Response({
#             'message': 'Usuário registrado com sucesso.',
#             'usuario': UsuarioSerializer(usuario).data,
#             'tokens': {
#                 'refresh': str(refresh),
#                 'access': str(refresh.access_token)
#             }
#         }, status=status.HTTP_201_CREATED)
    
#     return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

'''
Por usar o DRF-YASG rodando junto com o SimpleJWT o YASG
quebra completamente o parser da requisição quando a view
não é uma classe'''
class RegisterView(APIView):
    permission_classes = [permissions.AllowAny]

    @swagger_auto_schema(request_body=RegistroSerializer)
    def post(self, request):
        serializer = RegistroSerializer(data=request.data)

        if serializer.is_valid():
            usuario = serializer.save()

            refresh = RefreshToken.for_user(usuario)

            return Response({
                'message': 'Usuário registrado com sucesso.',
                'usuario': UsuarioSerializer(usuario).data,
                'tokens': {
                    'refresh': str(refresh),
                    'access': str(refresh.access_token)
                }
            }, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

# @api_view(['GET'])
# @permission_classes([permissions.IsAuthenticated])
# @swagger_auto_schema(request_body=UsuarioSerializer)
# def usuario_atual_view(request):
#     serializer = UsuarioSerializer(request.user)
#     return Response(serializer.data, status=status.HTTP_200_OK)

class UsuarioAtualView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    @swagger_auto_schema(responses={200: UsuarioSerializer()})
    def get(self, request):
        serializer = UsuarioSerializer(request.user)
        return Response(serializer.data, status=status.HTTP_200_OK)