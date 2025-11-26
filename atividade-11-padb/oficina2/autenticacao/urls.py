from django.urls import path
from .views import (
    RegisterView,
    UsuarioAtualView,
)
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

urlpatterns = [
    path('registro/', RegisterView.as_view(), name='registro'),
    path('login/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('usuario/', UsuarioAtualView.as_view(), name='usuario_atual'),
]
