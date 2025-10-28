from rest_framework import serializers
# from django.contrib.auth.models import User
from .models import MeuUsuario

class MeuUsuarioSerializer(serializers.ModelSerializer):
    class Meta:
        model = MeuUsuario
        fields = ['id', 'username', 'password', 'email']