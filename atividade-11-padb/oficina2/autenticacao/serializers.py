from rest_framework import serializers
from .models import Usuario, PerfilUsuario

class PerfilUsuarioSerializer(serializers.ModelSerializer):
    tipo_display = serializers.CharField(source='get_tipo_perfil_display', read_only=True)

    class Meta:
        model = PerfilUsuario
        fields = ['id', 'tipo_perfil', 'tipo_display']


class UsuarioSerializer(serializers.ModelSerializer):
    perfil = PerfilUsuarioSerializer(read_only=True)

    class Meta:
        model = Usuario
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'telefone', 'perfil']


class RegistroSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=6)
    password_confirm = serializers.CharField(write_only=True, min_length=6)
    tipo_perfil = serializers.ChoiceField(choices=PerfilUsuario.TIPOS_PERFIL, write_only=True)

    class Meta:
        model = Usuario
        fields = ['username', 'email', 'first_name', 'last_name', 'telefone', 'cpf', 'password', 'password_confirm', 'tipo_perfil']

    def validate(self, data):
        if data['password'] != data['password_confirm']:
            raise serializers.ValidationError("As senhas não coincidem.")
        return data

    def create(self, validated_data):
        password = validated_data.pop('password')
        validated_data.pop('password_confirm')
        tipo_perfil = validated_data.pop('tipo_perfil')

        user = Usuario.objects.create_user(**validated_data, password=password)

        PerfilUsuario.objects.create(usuario=user, tipo_perfil=tipo_perfil)

        return user