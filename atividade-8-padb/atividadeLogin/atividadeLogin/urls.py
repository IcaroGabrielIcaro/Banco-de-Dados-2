from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from api import views
from rest_framework_simplejwt.views import TokenRefreshView

router = DefaultRouter()
router.register(r'usuarios', views.UsuarioViewSet)
router.register(r'projetos', views.ProjetoViewSet)
router.register(r'tarefas', views.TarefaViewSet)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include(router.urls)),

    path('api/cadastro/', views.UsuarioRegisterView.as_view(), name='usuario-register'),
    path('api/login/', views.UsuarioTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]