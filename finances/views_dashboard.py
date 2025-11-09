"""
ViewSet para endpoints de dashboard y análisis financiero avanzado.

Endpoints disponibles:
- GET /api/finances/dashboard/overview/
- GET /api/finances/dashboard/trends/
- GET /api/finances/dashboard/categories/
- GET /api/finances/dashboard/patterns/
- GET /api/finances/dashboard/prediction/
- GET /api/finances/dashboard/budget-health/
"""

from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema, OpenApiParameter
from drf_spectacular.types import OpenApiTypes

from finances.services.analytics_service import FinancialAnalyticsService
from finances.serializers_dashboard import (
    DateRangeSerializer,
    MonthlyTrendsSerializer,
    CategoryBreakdownSerializer,
    SpendingPatternsSerializer,
    PredictionSerializer,
    BudgetHealthSerializer,
)
from core.utils import success_response, error_response


class DashboardViewSet(viewsets.ViewSet):
    """
    ViewSet para análisis financiero y dashboard.
    
    Proporciona endpoints para obtener estadísticas, tendencias,
    predicciones y análisis avanzados de las finanzas del usuario.
    """
    permission_classes = [permissions.IsAuthenticated]

    @extend_schema(
        summary="Resumen financiero general",
        description="Obtiene un resumen completo de ingresos, gastos, balance y promedios del usuario",
        parameters=[
            OpenApiParameter(
                name='start_date',
                type=OpenApiTypes.DATE,
                location=OpenApiParameter.QUERY,
                description='Fecha inicial del periodo (formato: YYYY-MM-DD)',
                required=False
            ),
            OpenApiParameter(
                name='end_date',
                type=OpenApiTypes.DATE,
                location=OpenApiParameter.QUERY,
                description='Fecha final del periodo (formato: YYYY-MM-DD)',
                required=False
            ),
        ],
        tags=['Dashboard']
    )
    @action(detail=False, methods=['get'], url_path='overview')
    def overview(self, request):
        """
        Resumen financiero general del usuario.
        
        Query params:
            - start_date: Fecha inicial (opcional)
            - end_date: Fecha final (opcional)
        
        Returns:
            Resumen con ingresos, gastos, balance, promedios y estadísticas
        """
        serializer = DateRangeSerializer(data=request.query_params)
        serializer.is_valid(raise_exception=True)

        start_date = serializer.validated_data.get('start_date')
        end_date = serializer.validated_data.get('end_date')

        try:
            data = FinancialAnalyticsService.get_overview(
                user=request.user,
                start_date=start_date,
                end_date=end_date
            )
            return success_response(
                data=data,
                message="Resumen financiero obtenido correctamente"
            )
        except Exception as e:
            return error_response(
                message="Error al obtener resumen financiero",
                errors={'detail': str(e)},
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @extend_schema(
        summary="Tendencias mensuales",
        description="Obtiene tendencias de ingresos y gastos por mes",
        parameters=[
            OpenApiParameter(
                name='months',
                type=OpenApiTypes.INT,
                location=OpenApiParameter.QUERY,
                description='Número de meses a analizar (1-36, default: 12)',
                required=False
            ),
        ],
        tags=['Dashboard']
    )
    @action(detail=False, methods=['get'], url_path='trends')
    def trends(self, request):
        """
        Tendencias mensuales de ingresos y gastos.
        
        Query params:
            - months: Número de meses a analizar (default: 12, max: 36)
        
        Returns:
            Lista de datos mensuales con ingresos, gastos y balance
        """
        serializer = MonthlyTrendsSerializer(data=request.query_params)
        serializer.is_valid(raise_exception=True)

        months = serializer.validated_data.get('months', 12)

        try:
            data = FinancialAnalyticsService.get_monthly_trends(
                user=request.user,
                months=months
            )
            return success_response(
                data=data,
                message=f"Tendencias de los últimos {months} meses obtenidas correctamente"
            )
        except Exception as e:
            return error_response(
                message="Error al obtener tendencias mensuales",
                errors={'detail': str(e)},
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @extend_schema(
        summary="Desglose por categorías",
        description="Obtiene la distribución de gastos/ingresos por categoría",
        parameters=[
            OpenApiParameter(
                name='category_type',
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                description='Tipo de categoría (income o expense)',
                required=False,
                enum=['income', 'expense']
            ),
            OpenApiParameter(
                name='start_date',
                type=OpenApiTypes.DATE,
                location=OpenApiParameter.QUERY,
                description='Fecha inicial (formato: YYYY-MM-DD)',
                required=False
            ),
            OpenApiParameter(
                name='end_date',
                type=OpenApiTypes.DATE,
                location=OpenApiParameter.QUERY,
                description='Fecha final (formato: YYYY-MM-DD)',
                required=False
            ),
        ],
        tags=['Dashboard']
    )
    @action(detail=False, methods=['get'], url_path='categories')
    def categories(self, request):
        """
        Desglose de transacciones por categoría.
        
        Query params:
            - category_type: 'income' o 'expense' (opcional)
            - start_date: Fecha inicial (opcional)
            - end_date: Fecha final (opcional)
        
        Returns:
            Lista de categorías con totales, porcentajes y promedios
        """
        serializer = CategoryBreakdownSerializer(data=request.query_params)
        serializer.is_valid(raise_exception=True)

        category_type = serializer.validated_data.get('category_type')
        start_date = serializer.validated_data.get('start_date')
        end_date = serializer.validated_data.get('end_date')

        try:
            data = FinancialAnalyticsService.get_category_breakdown(
                user=request.user,
                category_type=category_type,
                start_date=start_date,
                end_date=end_date
            )
            return success_response(
                data=data,
                message="Desglose por categorías obtenido correctamente"
            )
        except Exception as e:
            return error_response(
                message="Error al obtener desglose de categorías",
                errors={'detail': str(e)},
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @extend_schema(
        summary="Patrones de gasto",
        description="Analiza patrones de gasto del usuario (día de semana, categorías frecuentes, etc)",
        parameters=[
            OpenApiParameter(
                name='days',
                type=OpenApiTypes.INT,
                location=OpenApiParameter.QUERY,
                description='Número de días a analizar (7-365, default: 90)',
                required=False
            ),
        ],
        tags=['Dashboard']
    )
    @action(detail=False, methods=['get'], url_path='patterns')
    def patterns(self, request):
        """
        Análisis de patrones de gasto.
        
        Query params:
            - days: Número de días a analizar (default: 90, max: 365)
        
        Returns:
            Patrones identificados: día de semana, categoría frecuente, promedios
        """
        serializer = SpendingPatternsSerializer(data=request.query_params)
        serializer.is_valid(raise_exception=True)

        days = serializer.validated_data.get('days', 90)

        try:
            data = FinancialAnalyticsService.get_spending_patterns(
                user=request.user,
                days=days
            )
            return success_response(
                data=data,
                message=f"Patrones de gasto de los últimos {days} días obtenidos correctamente"
            )
        except Exception as e:
            return error_response(
                message="Error al obtener patrones de gasto",
                errors={'detail': str(e)},
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @extend_schema(
        summary="Predicción de gastos",
        description="Predice los gastos del próximo mes basándose en histórico",
        parameters=[
            OpenApiParameter(
                name='months_to_analyze',
                type=OpenApiTypes.INT,
                location=OpenApiParameter.QUERY,
                description='Meses históricos a considerar (3-12, default: 6)',
                required=False
            ),
        ],
        tags=['Dashboard']
    )
    @action(detail=False, methods=['get'], url_path='prediction')
    def prediction(self, request):
        """
        Predicción de gastos mensuales.
        
        Query params:
            - months_to_analyze: Meses históricos a considerar (default: 6, max: 12)
        
        Returns:
            Predicción de gastos totales y por categoría, con tendencia
        """
        serializer = PredictionSerializer(data=request.query_params)
        serializer.is_valid(raise_exception=True)

        months_to_analyze = serializer.validated_data.get('months_to_analyze', 6)

        try:
            data = FinancialAnalyticsService.predict_monthly_expenses(
                user=request.user,
                months_to_analyze=months_to_analyze
            )
            return success_response(
                data=data,
                message="Predicción de gastos obtenida correctamente"
            )
        except Exception as e:
            return error_response(
                message="Error al generar predicción de gastos",
                errors={'detail': str(e)},
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @extend_schema(
        summary="Salud de presupuestos",
        description="Evalúa el estado actual de los presupuestos del usuario",
        parameters=[
            OpenApiParameter(
                name='month',
                type=OpenApiTypes.DATE,
                location=OpenApiParameter.QUERY,
                description='Mes a evaluar (formato: YYYY-MM-DD, default: mes actual)',
                required=False
            ),
        ],
        tags=['Dashboard']
    )
    @action(detail=False, methods=['get'], url_path='budget-health')
    def budget_health(self, request):
        """
        Evaluación de salud de presupuestos.
        
        Query params:
            - month: Mes a evaluar (default: mes actual)
        
        Returns:
            Estado de presupuestos con porcentajes, alertas y recomendaciones
        """
        serializer = BudgetHealthSerializer(data=request.query_params)
        serializer.is_valid(raise_exception=True)

        month = serializer.validated_data.get('month')

        try:
            data = FinancialAnalyticsService.get_budget_health(
                user=request.user,
                month=month
            )
            return success_response(
                data=data,
                message="Estado de presupuestos obtenido correctamente"
            )
        except Exception as e:
            return error_response(
                message="Error al evaluar salud de presupuestos",
                errors={'detail': str(e)},
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )