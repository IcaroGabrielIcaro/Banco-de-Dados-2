from django.urls import path
from .views import (
    CursoViewSet,
    ModuloViewSet,
    AulaViewSet,
    MatriculaViewSet,
)

urlpatterns = [
    path('cursos/', CursoViewSet.as_view({'get': 'list', 'post': 'create'}), name='curso-list-create'),
    path('cursos/<int:pk>/', CursoViewSet.as_view({'get': 'retrieve', 'put': 'update', 'delete': 'destroy'}), name='curso-detail'),
    path('cursos/<int:pk>/modulos/', CursoViewSet.as_view({'get': 'modulos'}), name='curso-modulos'),
    path('modulos/', ModuloViewSet.as_view({'get': 'list', 'post': 'create'}), name='modulo-list-create'),
    path('modulos/<int:pk>/', ModuloViewSet.as_view({'get': 'retrieve', 'put': 'update', 'delete': 'destroy'}), name='modulo-detail'),
    path('modulos/<int:pk>/aulas/', ModuloViewSet.as_view({'get': 'aulas'}), name='modulo-aulas'),
    path('aulas/', AulaViewSet.as_view({'get': 'list', 'post': 'create'}), name='aula-list-create'),
    path('aulas/<int:pk>/', AulaViewSet.as_view({'get': 'retrieve', 'put': 'update', 'delete': 'destroy'}), name='aula-detail'),
    path('matriculas/', MatriculaViewSet.as_view({'get': 'list', 'post': 'create'}), name='matricula-list-create'),
    path('matriculas/<int:pk>/', MatriculaViewSet.as_view({'get': 'retrieve', 'put': 'update', 'delete': 'destroy'}), name='matricula-detail'),
]