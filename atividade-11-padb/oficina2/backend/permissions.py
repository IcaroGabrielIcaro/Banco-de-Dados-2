from rest_framework.permissions import BasePermission

class IsInstrutor(BasePermission):
    def has_permission(self, request, view):
        return request.user.perfilusuario.tipo_perfil == 'instrutor'


class IsAluno(BasePermission):
    def has_permission(self, request, view):
        return request.user.perfilusuario.tipo_perfil == 'aluno'
