from django.contrib import admin
from django.urls import path, include
from rest_framework_nested import routers
from api import views
from rest_framework_simplejwt.views import TokenRefreshView

router = routers.SimpleRouter()
router.register(r'usuarios', views.UsuarioViewSet, basename='usuarios')
router.register(r'projetos', views.ProjetoViewSet, basename='projetos')
router.register(r'tarefas', views.TarefaViewSet, basename='tarefas')

projetos_router = routers.NestedSimpleRouter(router, r'projetos', lookup='projeto')
projetos_router.register(r'tarefas', views.TarefaViewSet, basename='projeto-tarefas')

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include(router.urls)),
    path('api/', include(projetos_router.urls)),

    path('api/cadastro/', views.UsuarioRegisterView.as_view(), name='usuario-register'),
    path('api/login/', views.UsuarioTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/logout/', views.LogoutView.as_view(), name='token_logout'),
    path('api/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]
