from rest_framework import serializers
from .models import Usuario, Instituicao

class UsuarioSerializer(serializers.ModelSerializer):
    ativo = serializers.BooleanField(default=True)
    
    class Meta:
        model = Usuario
        fields = '__all__'

class InstituicaoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Instituicao
        fields = '__all__'