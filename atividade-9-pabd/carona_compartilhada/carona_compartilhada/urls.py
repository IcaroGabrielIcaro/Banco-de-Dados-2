from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from backend import views
from rest_framework_simplejwt.views import TokenRefreshView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('backend.urls')),
    path('api-auth/', include('rest_framework.urls')),

    path('api/cadastro/', views.UsuarioRegisterView.as_view(), name='usuario-register'),
    path('api/login/', views.UsuarioTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/logout/', views.LogoutView.as_view(), name='token_logout'),
    path('api/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)