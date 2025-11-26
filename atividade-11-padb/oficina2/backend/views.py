from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from .models import Curso, Modulo, Aula, Matricula
from .serializers import (
    CursoSerializer, CursoCreateSerializer,
    ModuloSerializer, ModuloCreateSerializer,
    AulaSerializer, AulaCreateSerializer,
    MatriculaSerializer, MatriculaCreateSerializer
)
from backend.permissions import IsInstrutor, IsAluno

class CursoViewSet(viewsets.ModelViewSet):
    queryset = Curso.objects.all()
    permission_classes = [IsAuthenticated]
    
    def get_serializer_class(self):
        if self.action in ['create']:
            return CursoCreateSerializer
        return CursoSerializer

    # ------ CREATE ------
    def create(self, request, *args, **kwargs):
        if request.user.perfilusuario.tipo_perfil != 'instrutor':
            return Response(
                {'error': 'Apenas instrutores podem criar cursos.'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        curso = serializer.save()
        
        return Response(CursoSerializer(curso).data, status=status.HTTP_201_CREATED)

    # ------ LISTA APENAS DO INSTRUTOR ------
    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated, IsInstrutor])
    def meus(self, request):
        cursos = Curso.objects.filter(instrutor=request.user)
        return Response(CursoSerializer(cursos, many=True).data)

    # ------ LISTAR MÓDULOS DE UM CURSO ------
    @action(detail=True, methods=['get'])
    def modulos(self, request, pk=None):
        curso = self.get_object()
        modulos = curso.modulos.all()
        return Response(ModuloSerializer(modulos, many=True).data)





class ModuloViewSet(viewsets.ModelViewSet):
    queryset = Modulo.objects.all()
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        if self.action == 'create':
            return ModuloCreateSerializer
        return ModuloSerializer

    # CREATE com validação de instrutor responsável
    def create(self, request, *args, **kwargs):
        serializer = ModuloCreateSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        modulo = serializer.save()
        return Response(ModuloSerializer(modulo).data, status=status.HTTP_201_CREATED)

    # ------ LISTAR AULAS DO MÓDULO ------
    @action(detail=True, methods=['get'])
    def aulas(self, request, pk=None):
        modulo = self.get_object()
        aulas = modulo.aulas.all()
        return Response(AulaSerializer(aulas, many=True).data)
    



class AulaViewSet(viewsets.ModelViewSet):
    queryset = Aula.objects.all()
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        if self.action == 'create':
            return AulaCreateSerializer
        return AulaSerializer

    def create(self, request, *args, **kwargs):
        serializer = AulaCreateSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        aula = serializer.save()
        return Response(AulaSerializer(aula).data, status=status.HTTP_201_CREATED)




class MatriculaViewSet(viewsets.ModelViewSet):
    queryset = Matricula.objects.all()
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        if self.action == 'create':
            return MatriculaCreateSerializer
        return MatriculaSerializer

    def create(self, request, *args, **kwargs):
        serializer = MatriculaCreateSerializer(
            data=request.data, 
            context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        matricula = serializer.save()
        return Response(MatriculaSerializer(matricula).data, status=status.HTTP_201_CREATED)

    # ------ LISTAR CURSOS QUE O ALUNO ESTÁ MATRICULADO ------
    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated, IsAluno])
    def meus(self, request):
        matriculas = Matricula.objects.filter(aluno=request.user)
        return Response(MatriculaSerializer(matriculas, many=True).data)