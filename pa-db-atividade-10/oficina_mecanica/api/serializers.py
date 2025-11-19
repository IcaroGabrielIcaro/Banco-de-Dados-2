from rest_framework import serializers
from .models import Usuario

class UsuarioSerializer(serializers.ModelSerializer):
    class Meta:
        model = Usuario
        fields = ['username',
            'email',
            'cpf',
            'telefone',
            'tipo_perfil',
            'password',]
        extra_kwargs = {
            'password': {'write_only': True},
            'data_cadastro': {'read_only': True},
             'telefone': {'required': False},
        }

    def create(self, validated_data):
        password = validated_data.pop('password', None)
        usuario = Usuario(**validated_data)

        if password:
            usuario.set_password(password)

        usuario.save()
        return usuario


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField()