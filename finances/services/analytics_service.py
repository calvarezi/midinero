"""
Servicio de análisis financiero avanzado.

Proporciona cálculos, agregaciones y predicciones sobre datos financieros del usuario.
"""

from django.db.models import Sum, Avg, Count, Q, F, Max, Min
from django.db.models.functions import TruncMonth, TruncWeek, TruncDay
from django.utils import timezone
from datetime import datetime, timedelta
from decimal import Decimal
from finances.models import Transaction, Category, Budget, FinancialGoal


class FinancialAnalyticsService:
    """
    Servicio centralizado para análisis financiero.
    
    Métodos disponibles:
    - get_overview: Resumen general del usuario
    - get_monthly_trends: Tendencias mensuales de ingresos y gastos
    - get_category_breakdown: Distribución por categorías
    - get_spending_patterns: Patrones de gasto
    - predict_monthly_expenses: Predicción de gastos
    """

    @staticmethod
    def get_overview(user, start_date=None, end_date=None):
        """
        Obtiene un resumen financiero completo del usuario.
        
        Args:
            user: Usuario autenticado
            start_date: Fecha inicial (opcional)
            end_date: Fecha final (opcional)
        
        Returns:
            dict: Resumen con ingresos, gastos, balance, y promedios
        """
        queryset = Transaction.objects.filter(user=user)
        
        if start_date:
            queryset = queryset.filter(date__gte=start_date)
        if end_date:
            queryset = queryset.filter(date__lte=end_date)

        # Agregaciones principales
        aggregates = queryset.aggregate(
            total_income=Sum('amount', filter=Q(category__type='income')),
            total_expense=Sum('amount', filter=Q(category__type='expense')),
            avg_income=Avg('amount', filter=Q(category__type='income')),
            avg_expense=Avg('amount', filter=Q(category__type='expense')),
            transaction_count=Count('id'),
            income_count=Count('id', filter=Q(category__type='income')),
            expense_count=Count('id', filter=Q(category__type='expense')),
            max_expense=Max('amount', filter=Q(category__type='expense')),
            min_expense=Min('amount', filter=Q(category__type='expense')),
        )

        total_income = Decimal(aggregates['total_income'] or 0)
        total_expense = Decimal(aggregates['total_expense'] or 0)
        balance = total_income - total_expense

        # Calcular tasa de ahorro
        savings_rate = 0
        if total_income > 0:
            savings_rate = float((balance / total_income) * 100)

        return {
            'total_income': float(total_income),
            'total_expense': float(total_expense),
            'balance': float(balance),
            'savings_rate': round(savings_rate, 2),
            'avg_income': float(aggregates['avg_income'] or 0),
            'avg_expense': float(aggregates['avg_expense'] or 0),
            'transaction_count': aggregates['transaction_count'],
            'income_count': aggregates['income_count'],
            'expense_count': aggregates['expense_count'],
            'max_expense': float(aggregates['max_expense'] or 0),
            'min_expense': float(aggregates['min_expense'] or 0),
            'period': {
                'start_date': start_date.isoformat() if start_date else None,
                'end_date': end_date.isoformat() if end_date else None,
            }
        }

    @staticmethod
    def get_monthly_trends(user, months=12):
        """
        Obtiene tendencias mensuales de ingresos y gastos.
        
        Args:
            user: Usuario autenticado
            months: Número de meses a analizar (default: 12)
        
        Returns:
            list: Lista de diccionarios con datos mensuales
        """
        start_date = timezone.now() - timedelta(days=months * 30)
        
        transactions = Transaction.objects.filter(
            user=user,
            date__gte=start_date
        ).annotate(
            month=TruncMonth('date')
        ).values('month').annotate(
            total_income=Sum('amount', filter=Q(category__type='income')),
            total_expense=Sum('amount', filter=Q(category__type='expense')),
            transaction_count=Count('id')
        ).order_by('month')

        trends = []
        for item in transactions:
            income = Decimal(item['total_income'] or 0)
            expense = Decimal(item['total_expense'] or 0)
            balance = income - expense
            
            trends.append({
                'month': item['month'].strftime('%Y-%m'),
                'month_name': item['month'].strftime('%B %Y'),
                'total_income': float(income),
                'total_expense': float(expense),
                'balance': float(balance),
                'transaction_count': item['transaction_count']
            })

        return trends

    @staticmethod
    def get_category_breakdown(user, category_type=None, start_date=None, end_date=None):
        """
        Obtiene el desglose por categorías.
        
        Args:
            user: Usuario autenticado
            category_type: 'income' o 'expense' (opcional, ambos si es None)
            start_date: Fecha inicial (opcional)
            end_date: Fecha final (opcional)
        
        Returns:
            list: Lista de categorías con totales y porcentajes
        """
        queryset = Transaction.objects.filter(user=user)
        
        if category_type:
            queryset = queryset.filter(category__type=category_type)
        if start_date:
            queryset = queryset.filter(date__gte=start_date)
        if end_date:
            queryset = queryset.filter(date__lte=end_date)

        # Agrupar por categoría
        category_data = queryset.values(
            'category__id',
            'category__name',
            'category__type'
        ).annotate(
            total=Sum('amount'),
            count=Count('id'),
            avg=Avg('amount')
        ).order_by('-total')

        # Calcular totales generales
        grand_total = sum(Decimal(item['total'] or 0) for item in category_data)

        # Calcular porcentajes
        breakdown = []
        for item in category_data:
            total = Decimal(item['total'] or 0)
            percentage = 0
            if grand_total > 0:
                percentage = float((total / grand_total) * 100)

            breakdown.append({
                'category_id': item['category__id'],
                'category_name': item['category__name'],
                'category_type': item['category__type'],
                'total': float(total),
                'percentage': round(percentage, 2),
                'transaction_count': item['count'],
                'average': float(item['avg'] or 0)
            })

        return breakdown

    @staticmethod
    def get_spending_patterns(user, days=90):
        """
        Analiza patrones de gasto del usuario.
        
        Args:
            user: Usuario autenticado
            days: Número de días a analizar (default: 90)
        
        Returns:
            dict: Patrones identificados (día de semana, categoría más frecuente, etc)
        """
        start_date = timezone.now() - timedelta(days=days)
        
        expenses = Transaction.objects.filter(
            user=user,
            category__type='expense',
            date__gte=start_date
        )

        # Análisis por día de la semana
        daily_spending = {}
        for expense in expenses:
            day_name = expense.date.strftime('%A')
            if day_name not in daily_spending:
                daily_spending[day_name] = {'total': Decimal(0), 'count': 0}
            daily_spending[day_name]['total'] += expense.amount
            daily_spending[day_name]['count'] += 1

        # Convertir a lista ordenada
        daily_pattern = [
            {
                'day': day,
                'total': float(data['total']),
                'count': data['count'],
                'average': float(data['total'] / data['count']) if data['count'] > 0 else 0
            }
            for day, data in daily_spending.items()
        ]

        # Categoría más frecuente
        top_category = expenses.values('category__name').annotate(
            count=Count('id'),
            total=Sum('amount')
        ).order_by('-count').first()

        # Gasto promedio diario
        total_expenses = expenses.aggregate(total=Sum('amount'))['total'] or Decimal(0)
        avg_daily = float(total_expenses / days) if days > 0 else 0

        return {
            'daily_pattern': daily_pattern,
            'most_frequent_category': top_category['category__name'] if top_category else None,
            'most_frequent_count': top_category['count'] if top_category else 0,
            'average_daily_spending': round(avg_daily, 2),
            'analysis_period_days': days,
        }

    @staticmethod
    def predict_monthly_expenses(user, months_to_analyze=6):
        """
        Predice gastos del próximo mes basándose en histórico.
        
        Args:
            user: Usuario autenticado
            months_to_analyze: Meses históricos a considerar (default: 6)
        
        Returns:
            dict: Predicción de gastos con desglose por categoría
        """
        start_date = timezone.now() - timedelta(days=months_to_analyze * 30)
        
        # Obtener gastos mensuales por categoría
        monthly_expenses = Transaction.objects.filter(
            user=user,
            category__type='expense',
            date__gte=start_date
        ).annotate(
            month=TruncMonth('date')
        ).values('category__id', 'category__name', 'month').annotate(
            monthly_total=Sum('amount')
        ).order_by('category__id', 'month')

        # Agrupar por categoría y calcular promedio manualmente
        category_data = {}
        for expense in monthly_expenses:
            cat_id = expense['category__id']
            cat_name = expense['category__name']
            amount = Decimal(expense['monthly_total'] or 0)
            
            if cat_id not in category_data:
                category_data[cat_id] = {
                    'category_id': cat_id,
                    'category_name': cat_name,
                    'totals': []
                }
            
            category_data[cat_id]['totals'].append(amount)

        # Calcular promedio por categoría
        predictions = []
        total_predicted = Decimal(0)

        for cat_id, data in category_data.items():
            if data['totals']:
                avg_amount = sum(data['totals']) / len(data['totals'])
                total_predicted += avg_amount
                
                predictions.append({
                    'category_id': data['category_id'],
                    'category_name': data['category_name'],
                    'predicted_amount': float(avg_amount),
                })

        # Ordenar por predicción descendente
        predictions.sort(key=lambda x: x['predicted_amount'], reverse=True)

        # Calcular tendencia (crecimiento o decrecimiento)
        recent_3_months = Transaction.objects.filter(
            user=user,
            category__type='expense',
            date__gte=timezone.now() - timedelta(days=90)
        ).aggregate(total=Sum('amount'))['total'] or Decimal(0)

        older_3_months = Transaction.objects.filter(
            user=user,
            category__type='expense',
            date__gte=timezone.now() - timedelta(days=180),
            date__lt=timezone.now() - timedelta(days=90)
        ).aggregate(total=Sum('amount'))['total'] or Decimal(0)

        trend = 'stable'
        trend_percentage = 0
        if older_3_months > 0:
            trend_percentage = float(((recent_3_months - older_3_months) / older_3_months) * 100)
            if trend_percentage > 5:
                trend = 'increasing'
            elif trend_percentage < -5:
                trend = 'decreasing'

        return {
            'predicted_total': float(total_predicted),
            'category_predictions': predictions,
            'trend': trend,
            'trend_percentage': round(trend_percentage, 2),
            'confidence': 'medium',
            'based_on_months': months_to_analyze,
        }

    @staticmethod
    def get_budget_health(user, month=None):
        """
        Evalúa la salud financiera basándose en presupuestos.
        
        Args:
            user: Usuario autenticado
            month: Fecha del mes a evaluar (default: mes actual)
        
        Returns:
            dict: Estado de presupuestos y recomendaciones
        """
        if not month:
            month = timezone.now().date().replace(day=1)

        budgets = Budget.objects.filter(user=user, month=month)
        
        budget_status = []
        total_budget = Decimal(0)
        total_spent = Decimal(0)

        for budget in budgets:
            spent = Transaction.objects.filter(
                user=user,
                category=budget.category,
                category__type='expense',
                date__year=month.year,
                date__month=month.month
            ).aggregate(total=Sum('amount'))['total'] or Decimal(0)

            percentage = 0
            if budget.limit_amount > 0:
                percentage = float((spent / budget.limit_amount) * 100)

            status = 'healthy'
            if percentage >= 100:
                status = 'exceeded'
            elif percentage >= 80:
                status = 'warning'

            budget_status.append({
                'category_name': budget.category.name,
                'limit': float(budget.limit_amount),
                'spent': float(spent),
                'remaining': float(budget.limit_amount - spent),
                'percentage': round(percentage, 2),
                'status': status
            })

            total_budget += budget.limit_amount
            total_spent += spent

        overall_status = 'healthy'
        if total_budget > 0:
            overall_percentage = float((total_spent / total_budget) * 100)
            if overall_percentage >= 100:
                overall_status = 'critical'
            elif overall_percentage >= 80:
                overall_status = 'warning'
        else:
            overall_percentage = 0

        return {
            'month': month.strftime('%Y-%m'),
            'overall_status': overall_status,
            'overall_percentage': round(overall_percentage, 2),
            'total_budget': float(total_budget),
            'total_spent': float(total_spent),
            'total_remaining': float(total_budget - total_spent),
            'budgets': budget_status,
            'has_budgets': len(budget_status) > 0
        }