# ===========================================
# RUTAS PRINCIPALES DEL PROYECTO
# ===========================================
# Este archivo centraliza todas las rutas del backend:
# - Administración de Django
# - Endpoints de usuarios (autenticación y perfiles)
# - Endpoints de finanzas (categorías y transacciones)
# - Documentación automática con drf-spectacular (Swagger / Redoc)
# ===========================================

from django.contrib import admin
from django.urls import path, include
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularSwaggerView,
    SpectacularRedocView,
)

# ===========================================
# PATRONES DE RUTAS PRINCIPALES
# ===========================================

urlpatterns = [
    # --------------------------
    # ADMINISTRACIÓN
    # --------------------------
    path("admin/", admin.site.urls),

    # --------------------------
    # API PRINCIPAL
    # --------------------------
    path("api/auth/", include("users.urls")),       # Autenticación y usuarios
    path("api/finances/", include("finances.urls")),  # Finanzas personales

    # --------------------------
    # DOCUMENTACIÓN DE LA API
    # --------------------------
    # Esquema base (OpenAPI 3)
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),

    # Swagger UI → interfaz interactiva para probar endpoints
    path(
        "api/docs/swagger/",
        SpectacularSwaggerView.as_view(url_name="schema"),
        name="swagger-ui",
    ),

    # Redoc → documentación detallada y elegante
    path(
        "api/docs/redoc/",
        SpectacularRedocView.as_view(url_name="schema"),
        name="redoc",
    ),
]

# ===========================================
# NOTAS DE DESARROLLO
# ===========================================
# 🔐 AUTENTICACIÓN (JWT - SimpleJWT)
#   POST   /api/auth/login/           → obtiene access y refresh tokens
#   POST   /api/auth/refresh/         → renueva el token de acceso
#   POST   /api/auth/logout/          → invalida el token de refresco
#   POST   /api/auth/register/        → crea un nuevo usuario
#   GET    /api/auth/profile/         → obtiene datos del usuario actual
#
# 💰 FINANZAS
#   /api/finances/categories/         → CRUD de categorías
#   /api/finances/transactions/       → CRUD de transacciones
#   /api/finances/transactions/summary/ → resumen financiero general
#
# 📘 DOCUMENTACIÓN
#   /api/docs/swagger/                → interfaz Swagger UI
#   /api/docs/redoc/                  → interfaz Redoc
#   /api/schema/                      → esquema OpenAPI (JSON/YAML)
# ===========================================
