"""
Tests para endpoints de dashboard y análisis financiero.
"""

from django.test import TestCase
from django.contrib.auth.models import User
from rest_framework.test import APIClient
from rest_framework import status
from datetime import datetime, timedelta
from decimal import Decimal

from finances.models import Category, Transaction, Budget, FinancialGoal


class DashboardOverviewTests(TestCase):
    """
    Tests para el endpoint de resumen general.
    """

    def setUp(self):
        """Configuración inicial para tests."""
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123',
            email='test@example.com'
        )
        self.client.force_authenticate(user=self.user)

        # Crear categorías
        self.cat_income = Category.objects.create(
            user=self.user,
            name='Salario',
            type='income'
        )
        self.cat_expense = Category.objects.create(
            user=self.user,
            name='Comida',
            type='expense'
        )

        # Crear transacciones de prueba
        Transaction.objects.create(
            user=self.user,
            category=self.cat_income,
            amount=Decimal('3000.00'),
            date=datetime.now()
        )
        Transaction.objects.create(
            user=self.user,
            category=self.cat_expense,
            amount=Decimal('500.00'),
            date=datetime.now()
        )
        Transaction.objects.create(
            user=self.user,
            category=self.cat_expense,
            amount=Decimal('800.00'),
            date=datetime.now()
        )

    def test_get_overview_success(self):
        """Verifica que el resumen general se obtenga correctamente."""
        response = self.client.get('/api/finances/dashboard/overview/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], 'success')
        
        data = response.data['data']
        self.assertEqual(data['total_income'], 3000.00)
        self.assertEqual(data['total_expense'], 1300.00)
        self.assertEqual(data['balance'], 1700.00)
        self.assertEqual(data['transaction_count'], 3)

    def test_get_overview_with_date_range(self):
        """Verifica que el filtro por fechas funcione correctamente."""
        start_date = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')
        end_date = datetime.now().strftime('%Y-%m-%d')
        
        response = self.client.get(
            f'/api/finances/dashboard/overview/?start_date={start_date}&end_date={end_date}'
        )
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('period', response.data['data'])

    def test_get_overview_requires_authentication(self):
        """Verifica que se requiera autenticación."""
        self.client.force_authenticate(user=None)
        response = self.client.get('/api/finances/dashboard/overview/')
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class DashboardTrendsTests(TestCase):
    """
    Tests para el endpoint de tendencias mensuales.
    """

    def setUp(self):
        """Configuración inicial para tests."""
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.client.force_authenticate(user=self.user)

        cat = Category.objects.create(
            user=self.user,
            name='Salario',
            type='income'
        )

        # Crear transacciones en diferentes meses
        for i in range(3):
            date = datetime.now() - timedelta(days=30 * i)
            Transaction.objects.create(
                user=self.user,
                category=cat,
                amount=Decimal('2000.00'),
                date=date
            )

    def test_get_trends_default(self):
        """Verifica que las tendencias se obtengan con parámetros default."""
        response = self.client.get('/api/finances/dashboard/trends/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(isinstance(response.data['data'], list))

    def test_get_trends_custom_months(self):
        """Verifica que se puedan especificar meses personalizados."""
        response = self.client.get('/api/finances/dashboard/trends/?months=6')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_trends_invalid_months(self):
        """Verifica validación de parámetro months."""
        response = self.client.get('/api/finances/dashboard/trends/?months=50')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class DashboardCategoriesTests(TestCase):
    """
    Tests para el endpoint de desglose por categorías.
    """

    def setUp(self):
        """Configuración inicial para tests."""
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.client.force_authenticate(user=self.user)

        # Crear múltiples categorías y transacciones
        cat1 = Category.objects.create(user=self.user, name='Comida', type='expense')
        cat2 = Category.objects.create(user=self.user, name='Transporte', type='expense')

        Transaction.objects.create(
            user=self.user,
            category=cat1,
            amount=Decimal('500.00'),
            date=datetime.now()
        )
        Transaction.objects.create(
            user=self.user,
            category=cat2,
            amount=Decimal('200.00'),
            date=datetime.now()
        )

    def test_get_categories_breakdown(self):
        """Verifica que el desglose por categorías funcione."""
        response = self.client.get('/api/finances/dashboard/categories/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(isinstance(response.data['data'], list))
        self.assertGreater(len(response.data['data']), 0)

    def test_get_categories_filtered_by_type(self):
        """Verifica filtro por tipo de categoría."""
        response = self.client.get('/api/finances/dashboard/categories/?category_type=expense')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        for item in response.data['data']:
            self.assertEqual(item['category_type'], 'expense')


class DashboardPatternsTests(TestCase):
    """
    Tests para el endpoint de patrones de gasto.
    """

    def setUp(self):
        """Configuración inicial para tests."""
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.client.force_authenticate(user=self.user)

        cat = Category.objects.create(user=self.user, name='Comida', type='expense')

        # Crear transacciones en diferentes días
        for i in range(5):
            Transaction.objects.create(
                user=self.user,
                category=cat,
                amount=Decimal('50.00'),
                date=datetime.now() - timedelta(days=i)
            )

    def test_get_spending_patterns(self):
        """Verifica que los patrones de gasto se obtengan."""
        response = self.client.get('/api/finances/dashboard/patterns/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('daily_pattern', response.data['data'])
        self.assertIn('average_daily_spending', response.data['data'])

    def test_get_patterns_custom_days(self):
        """Verifica que se puedan especificar días personalizados."""
        response = self.client.get('/api/finances/dashboard/patterns/?days=30')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class DashboardPredictionTests(TestCase):
    """
    Tests para el endpoint de predicción de gastos.
    """

    def setUp(self):
        """Configuración inicial para tests."""
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.client.force_authenticate(user=self.user)

        cat = Category.objects.create(user=self.user, name='Comida', type='expense')

        # Crear transacciones históricas
        for i in range(6):
            date = datetime.now() - timedelta(days=30 * i)
            Transaction.objects.create(
                user=self.user,
                category=cat,
                amount=Decimal('1000.00'),
                date=date
            )

    def test_get_prediction(self):
        """Verifica que la predicción se genere correctamente."""
        response = self.client.get('/api/finances/dashboard/prediction/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('predicted_total', response.data['data'])
        self.assertIn('category_predictions', response.data['data'])
        self.assertIn('trend', response.data['data'])


class DashboardBudgetHealthTests(TestCase):
    """
    Tests para el endpoint de salud de presupuestos.
    """

    def setUp(self):
        """Configuración inicial para tests."""
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.client.force_authenticate(user=self.user)

        cat = Category.objects.create(user=self.user, name='Comida', type='expense')
        
        # Crear presupuesto
        month = datetime.now().date().replace(day=1)
        Budget.objects.create(
            user=self.user,
            category=cat,
            month=month,
            limit_amount=Decimal('1000.00')
        )

        # Crear transacciones
        Transaction.objects.create(
            user=self.user,
            category=cat,
            amount=Decimal('600.00'),
            date=datetime.now()
        )

    def test_get_budget_health(self):
        """Verifica que la salud del presupuesto se evalúe."""
        response = self.client.get('/api/finances/dashboard/budget-health/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('overall_status', response.data['data'])
        self.assertIn('budgets', response.data['data'])
        self.assertTrue(response.data['data']['has_budgets'])