from rest_framework import serializers
from .models import Usuario, PerfilUsuario, Veiculo, Carona, Solicitacao, Avaliacao, Chat
from django.contrib.auth.password_validation import validate_password
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.tokens import RefreshToken, TokenError

class UsuarioRegisterSerializer(serializers.ModelSerializer):
    telefone = serializers.CharField(write_only=True, required=False)
    foto = serializers.ImageField(write_only=True, required=False, allow_null=True)
    biografia = serializers.CharField(write_only=True, required=False, allow_blank=True)
    tipo = serializers.ChoiceField(choices=Usuario.TIPO_CHOICES)

    class Meta:
        model = Usuario
        fields = ['username', 'email', 'password', 'tipo', 'telefone', 'foto', 'biografia']
        extra_kwargs = {
            'password': {'write_only': True},
            'email': {'required': True},
        }

    def create(self, validated_data):
        telefone = validated_data.pop('telefone', '')
        foto = validated_data.pop('foto', None)
        biografia = validated_data.pop('biografia', '')
        
        user = Usuario.objects.create_user(**validated_data)

        PerfilUsuario.objects.create(
            usuario=user,
            telefone=telefone,
            foto=foto,
            biografia=biografia
        )

        return user


class PerfilUsuarioSerializer(serializers.ModelSerializer):
    class Meta:
        model = PerfilUsuario
        fields = ['telefone', 'foto', 'biografia', 'verificado', 'nota_media']


class UsuarioSerializer(serializers.ModelSerializer):
    perfil = PerfilUsuarioSerializer(read_only=True)
    
    class Meta:
        model = Usuario
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'tipo', 'perfil']
        read_only_fields = ['id']


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


class VeiculoSerializer(serializers.ModelSerializer):
    motorista_nome = serializers.CharField(source='motorista.username', read_only=True)
    
    class Meta:
        model = Veiculo
        fields = [
            'id', 'motorista', 'motorista_nome', 'modelo', 'marca', 
            'cor', 'ano', 'placa', 'num_lugares', 'ativo'
        ]
        read_only_fields = ['id']


class CaronaSerializer(serializers.ModelSerializer):
    motorista_nome = serializers.CharField(source='motorista.username', read_only=True)
    veiculo_info = serializers.CharField(source='veiculo.__str__', read_only=True)
    
    class Meta:
        model = Carona
        fields = [
            'id', 'motorista', 'motorista_nome', 'veiculo', 'veiculo_info',
            'origem', 'destino', 'data_hora_saida', 'vagas_disponiveis',
            'preco_por_pessoa', 'observacoes', 'status', 'criado_em'
        ]
        read_only_fields = ['id', 'criado_em']


class SolicitacaoSerializer(serializers.ModelSerializer):
    passageiro_nome = serializers.CharField(source='passageiro.username', read_only=True)
    carona_info = serializers.CharField(source='carona.__str__', read_only=True)
    
    class Meta:
        model = Solicitacao
        fields = [
            'id', 'carona', 'carona_info', 'passageiro', 'passageiro_nome',
            'num_lugares', 'status', 'data_solicitacao'
        ]
        read_only_fields = ['id', 'data_solicitacao']


class AvaliacaoSerializer(serializers.ModelSerializer):
    avaliador_nome = serializers.CharField(source='avaliador.username', read_only=True)
    avaliado_nome = serializers.CharField(source='avaliado.username', read_only=True)
    
    class Meta:
        model = Avaliacao
        fields = [
            'id', 'carona', 'avaliador', 'avaliador_nome', 
            'avaliado', 'avaliado_nome', 'nota', 'comentario', 
            'tipo', 'criado_em'
        ]
        read_only_fields = ['id', 'criado_em']


class ChatSerializer(serializers.ModelSerializer):
    usuario_nome = serializers.CharField(source='usuario.username', read_only=True)
    
    class Meta:
        model = Chat
        fields = ['id', 'carona', 'usuario', 'usuario_nome', 'mensagem', 'data_hora']
        read_only_fields = ['id', 'data_hora']