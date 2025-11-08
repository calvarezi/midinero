# ===========================================
# RUTAS DE LA APP "finances"
# ===========================================
# Este archivo define todas las rutas relacionadas con:
# - Categorías (ingresos / gastos)
# - Transacciones
# - Resumen financiero (integrado en TransactionViewSet)
#
# Usa el enrutador de Django REST Framework para generar automáticamente:
#   - Rutas CRUD (list, create, retrieve, update, delete)
#   - Rutas personalizadas (summary)
# ===========================================

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CategoryViewSet, TransactionViewSet, NotificationViewSet, UserSettingsViewSet, BudgetViewSet, FinancialGoalViewSet

# ===========================================
# Router principal de la app
# ===========================================
# El router genera las rutas automáticamente según los viewsets.
#
# Estructura base:
#   /api/finances/categories/           → listar y crear categorías
#   /api/finances/categories/{id}/      → obtener, actualizar o eliminar
#   /api/finances/transactions/         → listar y crear transacciones
#   /api/finances/transactions/{id}/    → obtener, actualizar o eliminar
#   /api/finances/transactions/summary/ → resumen general del usuario
# ===========================================

router = DefaultRouter()
router.register(r'categories', CategoryViewSet, basename='category')
router.register(r'transactions', TransactionViewSet, basename='transaction')
router.register(r'budgets', BudgetViewSet, basename='budget')
router.register('goals', FinancialGoalViewSet, basename='financialgoal')
router.register('notifications', NotificationViewSet, basename='notification'),
router.register('settings', UserSettingsViewSet, basename='usersettings')

# ===========================================
# URL patterns
# ===========================================
# Se incluyen las rutas generadas automáticamente.
# No es necesario registrar endpoints manuales como "summary",
# ya que está implementado dentro del TransactionViewSet.
# ===========================================

urlpatterns = [
    path('', include(router.urls)),
]

# ===========================================
# EJEMPLOS DE USO (para documentación y pruebas)
# ===========================================
# Categorías
#   GET    /api/finances/categories/           → lista de categorías del usuario
#   POST   /api/finances/categories/           → crear nueva categoría
#   GET    /api/finances/categories/{id}/      → obtener una categoría
#   PUT    /api/finances/categories/{id}/      → actualizar una categoría
#   DELETE /api/finances/categories/{id}/      → eliminar una categoría
#
# Transacciones
#   GET    /api/finances/transactions/         → lista de transacciones del usuario
#   POST   /api/finances/transactions/         → crear nueva transacción
#   GET    /api/finances/transactions/{id}/    → obtener una transacción
#   PUT    /api/finances/transactions/{id}/    → actualizar una transacción
#   DELETE /api/finances/transactions/{id}/    → eliminar una transacción
#
# Resumen financiero
#   GET    /api/finances/transactions/summary/ → obtener resumen (ingresos, gastos, balance)
# ===========================================
