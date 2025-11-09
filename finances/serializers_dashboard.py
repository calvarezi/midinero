"""
Serializers para endpoints de dashboard y análisis.

Validan parámetros de entrada y formatean respuestas de análisis financiero.
"""

from rest_framework import serializers
from datetime import datetime


class DateRangeSerializer(serializers.Serializer):
    """
    Validador para rangos de fechas en consultas de análisis.
    """
    start_date = serializers.DateField(required=False, allow_null=True)
    end_date = serializers.DateField(required=False, allow_null=True)

    def validate(self, attrs):
        """
        Valida que la fecha de inicio sea anterior a la fecha final.
        """
        start_date = attrs.get('start_date')
        end_date = attrs.get('end_date')

        if start_date and end_date:
            if start_date > end_date:
                raise serializers.ValidationError(
                    "La fecha de inicio debe ser anterior a la fecha final."
                )

        return attrs


class MonthlyTrendsSerializer(serializers.Serializer):
    """
    Validador para parámetros de tendencias mensuales.
    """
    months = serializers.IntegerField(
        required=False,
        default=12,
        min_value=1,
        max_value=36,
        help_text="Número de meses a analizar (1-36)"
    )


class CategoryBreakdownSerializer(serializers.Serializer):
    """
    Validador para parámetros de desglose por categorías.
    """
    category_type = serializers.ChoiceField(
        choices=['income', 'expense'],
        required=False,
        allow_null=True,
        help_text="Tipo de categoría a filtrar"
    )
    start_date = serializers.DateField(required=False, allow_null=True)
    end_date = serializers.DateField(required=False, allow_null=True)

    def validate(self, attrs):
        """
        Valida que el rango de fechas sea correcto.
        """
        start_date = attrs.get('start_date')
        end_date = attrs.get('end_date')

        if start_date and end_date:
            if start_date > end_date:
                raise serializers.ValidationError(
                    "La fecha de inicio debe ser anterior a la fecha final."
                )

        return attrs


class SpendingPatternsSerializer(serializers.Serializer):
    """
    Validador para parámetros de análisis de patrones de gasto.
    """
    days = serializers.IntegerField(
        required=False,
        default=90,
        min_value=7,
        max_value=365,
        help_text="Número de días a analizar (7-365)"
    )


class PredictionSerializer(serializers.Serializer):
    """
    Validador para parámetros de predicción de gastos.
    """
    months_to_analyze = serializers.IntegerField(
        required=False,
        default=6,
        min_value=3,
        max_value=12,
        help_text="Meses históricos a considerar (3-12)"
    )


class BudgetHealthSerializer(serializers.Serializer):
    """
    Validador para parámetros de salud de presupuestos.
    """
    month = serializers.DateField(
        required=False,
        allow_null=True,
        help_text="Mes a evaluar (formato YYYY-MM-DD)"
    )


class OverviewResponseSerializer(serializers.Serializer):
    """
    Serializer de respuesta para overview financiero.
    Solo para documentación, no se usa en validación.
    """
    total_income = serializers.DecimalField(max_digits=12, decimal_places=2)
    total_expense = serializers.DecimalField(max_digits=12, decimal_places=2)
    balance = serializers.DecimalField(max_digits=12, decimal_places=2)
    savings_rate = serializers.FloatField()
    avg_income = serializers.DecimalField(max_digits=12, decimal_places=2)
    avg_expense = serializers.DecimalField(max_digits=12, decimal_places=2)
    transaction_count = serializers.IntegerField()
    income_count = serializers.IntegerField()
    expense_count = serializers.IntegerField()
    max_expense = serializers.DecimalField(max_digits=12, decimal_places=2)
    min_expense = serializers.DecimalField(max_digits=12, decimal_places=2)


class MonthlyTrendItemSerializer(serializers.Serializer):
    """
    Serializer para un item de tendencia mensual.
    """
    month = serializers.CharField()
    month_name = serializers.CharField()
    total_income = serializers.DecimalField(max_digits=12, decimal_places=2)
    total_expense = serializers.DecimalField(max_digits=12, decimal_places=2)
    balance = serializers.DecimalField(max_digits=12, decimal_places=2)
    transaction_count = serializers.IntegerField()


class CategoryBreakdownItemSerializer(serializers.Serializer):
    """
    Serializer para un item de desglose de categoría.
    """
    category_id = serializers.IntegerField()
    category_name = serializers.CharField()
    category_type = serializers.CharField()
    total = serializers.DecimalField(max_digits=12, decimal_places=2)
    percentage = serializers.FloatField()
    transaction_count = serializers.IntegerField()
    average = serializers.DecimalField(max_digits=12, decimal_places=2)