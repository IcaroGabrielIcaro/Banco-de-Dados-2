from rest_framework import serializers
from .models import Usuario, Projeto, Tarefa
from django.contrib.auth.password_validation import validate_password
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.tokens import RefreshToken, TokenError

class UsuarioRegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    password2 = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = Usuario
        fields = ['id', 'username', 'email', 'bio', 'password', 'password2']

    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({"password": "As senhas não coincidem."})
        return attrs

    def create(self, validated_data):
        password = validated_data.pop('password')
        validated_data.pop('password2')
        user = Usuario(**validated_data)
        user.set_password(password)
        user.save()
        return user


class UsuarioSerializer(serializers.ModelSerializer):
    class Meta:
        model = Usuario
        fields = ['id', 'username', 'email', 'bio', 'data_cadastro']


class LogoutSerializer(serializers.Serializer):
    refresh = serializers.CharField()

    def validate(self, attrs):
        self.token = attrs['refresh']
        return attrs

    def save(self, **kwargs):
        try:
            token = RefreshToken(self.token)
            token.blacklist()
        except TokenError:
            self.fail("Token inválido ou já expirado.")


class UsuarioTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token["email"] = getattr(user, "email", "")
        token["username"] = getattr(user, "username", "")
        return token

    def validate(self, attrs):
        try:
            data = super().validate(attrs)
        except serializers.ValidationError as e:
            raise e
        except Exception as e:
            raise serializers.ValidationError(
                {"detail": f"Erro interno durante autenticação: {str(e)}"}
            )

        try:
            data["user"] = UsuarioSerializer(self.user).data
        except Exception:
            data["user"] = {
                "id": self.user.id,
                "username": self.user.username,
                "email": getattr(self.user, "email", ""),
            }

        return data


class ProjetoSerializer(serializers.ModelSerializer):
    usuario = serializers.StringRelatedField(read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)

    class Meta:
        model = Projeto
        fields = [
            'id',
            'nome',
            'descricao',
            'usuario',
            'data_criacao',
            'data_atualizacao',
            'status',
            'status_display',
        ]
        read_only_fields = ['usuario', 'data_criacao', 'data_atualizacao']


class TarefaSerializer(serializers.ModelSerializer):
    projeto_nome = serializers.CharField(source='projeto.nome', read_only=True)
    prioridade_display = serializers.CharField(source='get_prioridade_display', read_only=True)

    class Meta:
        model = Tarefa
        fields = [
            'id',
            'titulo',
            'descricao',
            'projeto',
            'projeto_nome',
            'concluida',
            'prioridade',
            'prioridade_display',
            'data_criacao',
            'data_conclusao',
        ]
        read_only_fields = ['data_criacao', 'data_conclusao']
