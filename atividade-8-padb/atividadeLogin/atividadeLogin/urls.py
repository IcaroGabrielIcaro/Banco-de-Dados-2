from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from api import views

router = DefaultRouter()
router.register(r'usuarios', views.UsuarioViewSet)
router.register(r'projetos', views.ProjetoViewSet)
router.register(r'tarefas', views.TarefaViewSet)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include(router.urls)),
]
