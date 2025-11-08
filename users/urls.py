# ===========================================
# RUTAS DE LA APP "users"
# ===========================================
# Este archivo define las rutas de autenticación y gestión de usuarios:
# - Registro de nuevos usuarios
# - Login con JWT
# - Refresh del token
# - Obtener perfil del usuario autenticado
# ===========================================

from django.urls import path
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)
from . import views

urlpatterns = [
    # ===========================================
    # AUTENTICACIÓN CON JWT
    # ===========================================
    # Estos endpoints los proporciona SimpleJWT:
    #
    # POST /api/auth/login/       → obtiene par de tokens (access + refresh)
    # POST /api/auth/refresh/     → renueva el token de acceso usando refresh
    # POST /api/auth/logout/      → invalida el token de refresh (logout seguro)
    # ===========================================

    path('login/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('logout/', views.LogoutView.as_view(), name='logout'),

    # ===========================================
    # REGISTRO DE USUARIOS NUEVOS
    # ===========================================
    # Endpoint personalizado para crear cuentas nuevas.
    # POST /api/auth/register/  → crea un nuevo usuario
    # ===========================================

    path('register/', views.RegisterView.as_view(), name='register'),

    # ===========================================
    # PERFIL DEL USUARIO AUTENTICADO
    # ===========================================
    # GET /api/auth/profile/  → devuelve los datos del usuario logueado
    # ===========================================

    path('profile/', views.ProfileView.as_view(), name='profile'),
]
