from rest_framework import serializers
from .models import Curso, Modulo, Aula, Matricula


class CursoSerializer(serializers.ModelSerializer):
    instrutor_nome = serializers.CharField(source='instrutor.get_full_name', read_only=True)

    class Meta:
        model = Curso
        fields = ['id', 'nome', 'descricao', 'data_criacao', 'instrutor', 'instrutor_nome']
        read_only_fields = ['instrutor', 'data_criacao']


class CursoCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Curso
        fields = ['nome', 'descricao']

    def create(self, validated_data):
        user = self.context['request'].user

        if not user.perfilusuario.tipo_perfil == 'instrutor':
            raise serializers.ValidationError("Apenas instrutores podem criar cursos.")

        return Curso.objects.create(instrutor=user, **validated_data)




class ModuloSerializer(serializers.ModelSerializer):
    curso_nome = serializers.CharField(source='curso.nome', read_only=True)

    class Meta:
        model = Modulo
        fields = ['id', 'curso', 'curso_nome', 'titulo', 'ordem']

    
class ModuloCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Modulo
        fields = ['curso', 'titulo', 'ordem']

    def validate(self, data):
        curso = data['curso']
        user = self.context['request'].user

        if curso.instrutor != user:
            raise serializers.ValidationError("Você não pode criar módulos em cursos que não são seus.")

        return data
    



class AulaSerializer(serializers.ModelSerializer):
    modulo_nome = serializers.CharField(source='modulo.titulo', read_only=True)

    class Meta:
        model = Aula
        fields = ['id', 'modulo', 'modulo_nome', 'titulo', 'conteudo', 'duracao', 'ordem']


class AulaCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Aula
        fields = ['modulo', 'titulo', 'conteudo', 'duracao', 'ordem']

    def validate(self, data):
        modulo = data['modulo']
        user = self.context['request'].user

        if modulo.curso.instrutor != user:
            raise serializers.ValidationError("Você não pode criar aulas em cursos que não são seus.")

        return data




class MatriculaSerializer(serializers.ModelSerializer):
    aluno_nome = serializers.CharField(source='aluno.get_full_name', read_only=True)
    curso_nome = serializers.CharField(source='curso.nome', read_only=True)

    class Meta:
        model = Matricula
        fields = ['id', 'aluno', 'aluno_nome', 'curso', 'curso_nome', 'data_matricula']
        read_only_fields = ['data_matricula']


class MatriculaCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Matricula
        fields = ['curso']

    def create(self, validated_data):
        user = self.context['request'].user

        if user.perfilusuario.tipo_perfil != 'aluno':
            raise serializers.ValidationError("Somente alunos podem se matricular.")

        curso = validated_data['curso']

        if Matricula.objects.filter(aluno=user, curso=curso).exists():
            raise serializers.ValidationError("Você já está matriculado neste curso.")

        return Matricula.objects.create(aluno=user, curso=curso)
