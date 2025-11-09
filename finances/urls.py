"""
Rutas de la app finances.

Incluye:
- CRUD de categorías, transacciones, presupuestos, metas
- Dashboard y análisis financiero
- Notificaciones
- Configuración de usuario
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    CategoryViewSet,
    TransactionViewSet,
    NotificationViewSet,
    UserSettingsViewSet,
    BudgetViewSet,
    FinancialGoalViewSet
)
from .views_dashboard import DashboardViewSet

router = DefaultRouter()

# CRUD endpoints
router.register(r'categories', CategoryViewSet, basename='category')
router.register(r'transactions', TransactionViewSet, basename='transaction')
router.register(r'budgets', BudgetViewSet, basename='budget')
router.register(r'goals', FinancialGoalViewSet, basename='financialgoal')
router.register(r'notifications', NotificationViewSet, basename='notification')
router.register(r'settings', UserSettingsViewSet, basename='usersettings')

# Dashboard endpoints
router.register(r'dashboard', DashboardViewSet, basename='dashboard')

urlpatterns = [
    path('', include(router.urls)),
]

"""
Endpoints disponibles:

CATEGORIAS:
- GET    /api/finances/categories/
- POST   /api/finances/categories/
- GET    /api/finances/categories/{id}/
- PUT    /api/finances/categories/{id}/
- PATCH  /api/finances/categories/{id}/
- DELETE /api/finances/categories/{id}/

TRANSACCIONES:
- GET    /api/finances/transactions/
- POST   /api/finances/transactions/
- GET    /api/finances/transactions/{id}/
- PUT    /api/finances/transactions/{id}/
- PATCH  /api/finances/transactions/{id}/
- DELETE /api/finances/transactions/{id}/
- GET    /api/finances/transactions/summary/
- GET    /api/finances/transactions/export/?format=csv|xlsx

PRESUPUESTOS:
- GET    /api/finances/budgets/
- POST   /api/finances/budgets/
- GET    /api/finances/budgets/{id}/
- PUT    /api/finances/budgets/{id}/
- PATCH  /api/finances/budgets/{id}/
- DELETE /api/finances/budgets/{id}/

METAS FINANCIERAS:
- GET    /api/finances/goals/
- POST   /api/finances/goals/
- GET    /api/finances/goals/{id}/
- PUT    /api/finances/goals/{id}/
- PATCH  /api/finances/goals/{id}/
- DELETE /api/finances/goals/{id}/
- POST   /api/finances/goals/{id}/add-amount/
- GET    /api/finances/goals/{id}/progress/
- GET    /api/finances/goals/export/?format=csv|xlsx

NOTIFICACIONES:
- GET    /api/finances/notifications/
- POST   /api/finances/notifications/
- GET    /api/finances/notifications/{id}/
- PUT    /api/finances/notifications/{id}/
- PATCH  /api/finances/notifications/{id}/
- DELETE /api/finances/notifications/{id}/
- POST   /api/finances/notifications/{id}/mark-read/
- POST   /api/finances/notifications/mark-all-read/
- POST   /api/finances/notifications/{id}/archive/
- POST   /api/finances/notifications/clear-read/
- POST   /api/finances/notifications/send-test-email/
- GET    /api/finances/notifications/summary/

CONFIGURACION:
- GET    /api/finances/settings/
- POST   /api/finances/settings/
- GET    /api/finances/settings/{id}/
- PUT    /api/finances/settings/{id}/
- PATCH  /api/finances/settings/{id}/

DASHBOARD Y ANALISIS:
- GET    /api/finances/dashboard/overview/
         Query params: start_date, end_date
         
- GET    /api/finances/dashboard/trends/
         Query params: months (default: 12, max: 36)
         
- GET    /api/finances/dashboard/categories/
         Query params: category_type, start_date, end_date
         
- GET    /api/finances/dashboard/patterns/
         Query params: days (default: 90, max: 365)
         
- GET    /api/finances/dashboard/prediction/
         Query params: months_to_analyze (default: 6, max: 12)
         
- GET    /api/finances/dashboard/budget-health/
         Query params: month (formato: YYYY-MM-DD)
"""