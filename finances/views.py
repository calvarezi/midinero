# ==========================================================
# IMPORTS - ORGANIZADOS Y CORREGIDOS
# ==========================================================

# Django / Python estándar
import csv
import io
from datetime import datetime, date

from django.db.models import Sum, Q
from django.db.models.functions import TruncMonth
from django.http import HttpResponse
from django.utils.dateparse import parse_date
from django.shortcuts import get_object_or_404

# Django REST Framework
from rest_framework import viewsets, permissions, status, generics, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend

# Librerías externas
from openpyxl import Workbook
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.units import cm

# ==========================================================
# MODELOS
# ==========================================================
from finances.models import (
    Category,
    Transaction,
    Budget,
    FinancialGoal,
    Notification,
    UserSettings,
)

# ==========================================================
# SERIALIZADORES
# ==========================================================
from finances.serializers import CategorySerializer, TransactionSerializer
from finances.serializers_budget import BudgetSerializer
from finances.serializers_notifications import NotificationSerializer
from finances.serializers_settings import UserSettingsSerializer
from finances.serializers_goals import FinancialGoalSerializer  # si existe este archivo

# ==========================================================
# SERVICIOS Y UTILIDADES
# ==========================================================
from finances.services.notifications_service import NotificationService
from finances.utils.email_utils import send_notification_email

# Utilidades globales del proyecto
from core.utils import success_response, error_response
from core.permissions import IsOwnerOrReadOnly



# ==========================================================
# CATEGORÍAS
# ==========================================================
class CategoryViewSet(viewsets.ModelViewSet):
    """
    Vista para gestionar categorías de ingresos y gastos.
    Cada usuario puede crear sus propias categorías personalizadas.
    """
    serializer_class = CategorySerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [filters.SearchFilter, DjangoFilterBackend]
    search_fields = ['name']
    filterset_fields = ['type']

    def get_queryset(self):
        """
        ✅ CORRECCIÓN: Agregar select_related aunque no sea crítico aquí
        Devuelve solo las categorías del usuario autenticado.
        """
        return (
            Category.objects
            .filter(user=self.request.user)
            .select_related('user')  
            .order_by('name')
        )

    def perform_create(self, serializer):
        """
        Asigna automáticamente el usuario a la nueva categoría.
        """
        serializer.save(user=self.request.user)

    def perform_destroy(self, instance):
        """
        VALIDACIÓN: Verificar si hay transacciones antes de eliminar.
        """
        transaction_count = instance.transactions.count()
        
        if transaction_count > 0:
            from rest_framework.exceptions import ValidationError
            raise ValidationError(
                f"No puedes eliminar esta categoría porque tiene {transaction_count} "
                "transacciones asociadas. Elimina primero las transacciones."
            )
        
        super().perform_destroy(instance)


# ==========================================================
# TRANSACCIONES
# ==========================================================
class TransactionViewSet(viewsets.ModelViewSet):
    """
    Vista para registrar, consultar y analizar transacciones.
    Incluye filtros, resumen financiero, actualización de metas y alertas automáticas de presupuesto.
    """
    serializer_class = TransactionSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['category__type', 'date']
    search_fields = ['category__name', 'description']
    ordering_fields = ['date', 'amount']
    ordering = ['-date']

    def get_queryset(self):
        """
        Optimizar con select_related 
        Devuelve las transacciones del usuario autenticado.
        """
        return (
            Transaction.objects
            .filter(user=self.request.user)
            .select_related('category', 'user')
            .order_by('-date')
        )

    def perform_create(self, serializer):
        """
        Crea la transacción y actualiza:
        - Notificaciones automáticas
        - Progreso de metas
        - Estado del presupuesto
        """
        # Guardar transacción con el usuario autenticado
        transaction = serializer.save(user=self.request.user)
        user = transaction.user
        month = transaction.date.replace(day=1)

        # ===================================
        # Notificación de transacción
        # ===================================
        try:
            NotificationService.create_transaction_notification(transaction)
        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Error creando notificación de transacción: {e}")

        # ===================================
        # Verificar si afecta a un presupuesto
        # ===================================
        if transaction.category.type == 'expense':  
            try:
                budget = Budget.objects.get(
                    user=user, 
                    category=transaction.category, 
                    month=month
                )
                budget.check_status()
            except Budget.DoesNotExist:
                pass  # 
            except Exception as e:
                import logging
                logger = logging.getLogger(__name__)
                logger.error(f"Error verificando presupuesto: {e}")

        # ===================================
        # progreso de metas financieras
        # ===================================
        try:
            goals = FinancialGoal.objects.filter(user=user, month=month)
            for goal in goals:
                self.update_goal_progress(goal)
        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Error actualizando metas: {e}")

    def update_goal_progress(self, goal):
        """
        Actualiza el progreso de una meta financiera basándose en transacciones.
        """
        user = goal.user
        month = goal.month

        # Calcular ingresos y gastos del mes
        total_income = user.transactions.filter(
            category__type='income',
            date__year=month.year,
            date__month=month.month
        ).aggregate(total=Sum('amount'))['total'] or Decimal('0')

        total_expense = user.transactions.filter(
            category__type='expense',
            date__year=month.year,
            date__month=month.month
        ).aggregate(total=Sum('amount'))['total'] or Decimal('0')

        # Ahorro = Ingresos - Gastos
        current_savings = total_income - total_expense
        goal.current_amount = current_savings

        # Verificar si se alcanzó la meta
        if current_savings >= goal.target_amount and not goal.achieved:
            goal.achieved = True
            
            # Enviar notificación
            try:
                NotificationService.create(
                    user=user,
                    type='GOAL_COMPLETED',
                    title=f"¡Meta alcanzada: {goal.name}!",
                    message=(
                        f"¡Felicidades! Has alcanzado tu meta '{goal.name}' "
                        f"de ${goal.target_amount:.2f}."
                    ),
                    priority='MEDIUM',
                    send_email=True
                )
            except Exception as e:
                import logging
                logger = logging.getLogger(__name__)
                logger.error(f"Error enviando notificación de meta: {e}")

        goal.save()

    @action(detail=False, methods=['get'], url_path='summary')
    def summary(self, request):
        """
        Devuelve el resumen financiero del usuario (ingresos, gastos, balance).
        Usar aggregate en una sola query
        """
        user = request.user
        
        # Optimización: Una sola query con aggregate
        totals = Transaction.objects.filter(user=user).aggregate(
            total_income=Sum('amount', filter=Q(category__type='income')),
            total_expense=Sum('amount', filter=Q(category__type='expense')),
        )

        # Convertir a Decimal para evitar errores con None
        total_income = Decimal(totals['total_income'] or 0)
        total_expense = Decimal(totals['total_expense'] or 0)

        data = {
            "total_income": float(total_income),
            "total_expense": float(total_expense),
            "balance": float(total_income - total_expense),
        }

        return success_response(
            data=data, 
            message="Resumen financiero obtenido correctamente."
        )

    # Exportar transacciones
    @action(detail=False, methods=['get'], url_path='export')
    def export(self, request):
        """
        Exporta las transacciones del usuario en formato CSV o XLSX.
        Uso: /api/finances/transactions/export/?format=csv
        """
        user = request.user
        formato = request.query_params.get('format', 'csv').lower()
        
        queryset = self.get_queryset()

        if not queryset.exists():
            return error_response(
                "No hay transacciones para exportar.", 
                status.HTTP_404_NOT_FOUND
            )

        if formato == 'csv':
            buffer = io.StringIO()
            writer = csv.writer(buffer)
            writer.writerow([
                "ID", "Fecha", "Categoría", "Tipo", "Monto", "Descripción"
            ])
            
            for t in queryset:
                writer.writerow([
                    t.id,
                    t.date.strftime("%Y-%m-%d %H:%M"),
                    t.category.name,
                    t.category.get_type_display(),
                    float(t.amount),
                    t.description
                ])
            
            response = HttpResponse(buffer.getvalue(), content_type='text/csv')
            response['Content-Disposition'] = (
                f'attachment; filename="transacciones_{user.username}.csv"'
            )
            return response

        elif formato == 'xlsx':
            from openpyxl import Workbook
            
            wb = Workbook()
            ws = wb.active
            ws.title = "Transacciones"
            
            # Encabezados
            ws.append(["ID", "Fecha", "Categoría", "Tipo", "Monto", "Descripción"])
            
            # Datos
            for t in queryset:
                ws.append([
                    t.id,
                    t.date.strftime("%Y-%m-%d %H:%M"),
                    t.category.name,
                    t.category.get_type_display(),
                    float(t.amount),
                    t.description
                ])
            
            buffer = io.BytesIO()
            wb.save(buffer)
            buffer.seek(0)
            
            response = HttpResponse(
                buffer.getvalue(),
                content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            )
            response['Content-Disposition'] = (
                f'attachment; filename="transacciones_{user.username}.xlsx"'
            )
            return response

        return error_response(
            "Formato no soportado. Usa 'csv' o 'xlsx'.", 
            status.HTTP_400_BAD_REQUEST
        )
# ==========================================================
# PRESUPUESTOS
# ==========================================================
class BudgetViewSet(viewsets.ModelViewSet):
    """
    Gestión de presupuestos mensuales por categoría.
    Permite crear, listar, actualizar y eliminar presupuestos.
    Verifica automáticamente si el gasto supera el límite.
    """
    serializer_class = BudgetSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """Retorna los presupuestos del usuario autenticado."""
        return Budget.objects.filter(user=self.request.user).select_related('category').order_by('-month')

    def perform_create(self, serializer):
        budget = serializer.save(user=self.request.user)
        self.update_budget_progress(budget)

    def perform_update(self, serializer):
        budget = serializer.save()
        self.update_budget_progress(budget)

    def update_budget_progress(self, budget):
        """Actualiza el gasto y envía notificación si se supera el límite."""
        user = budget.user
        month = budget.month
        category = budget.category

        # Calcular total gastado en la categoría durante el mes
        spent = (
            Transaction.objects.filter(
                user=user,
                category=category,
                category__type='expense',
                date__year=month.year,
                date__month=month.month
            ).aggregate(total=Sum('amount'))['total'] or 0
        )

        # No guardamos 'spent_amount' en DB, es calculado en serializer
        # budget.spent_amount = spent
        # budget.save()

        # Verificar si supera el presupuesto
        if budget.notify_when_exceeded and spent > budget.limit_amount:
            NotificationService.create(
                user=user,
                type='BUDGET_EXCEEDED',
                title=f"Presupuesto superado: {category.name}",
                message=(
                    f"Has superado el presupuesto de ${budget.limit_amount:.2f} "
                    f"para la categoría '{category.name}'. Gastaste ${spent:.2f}."
                ),
                priority='HIGH',
                send_email=True
            )

    def list(self, request, *args, **kwargs):
        """Lista los presupuestos del usuario autenticado con formato uniforme."""
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return success_response(data=serializer.data, message="Presupuestos obtenidos correctamente.")

# ==========================================================
# METAS FINANCIERAS
# ==========================================================



class FinancialGoalViewSet(viewsets.ModelViewSet):
    """
    Gestión de múltiples metas financieras mensuales.
    Permite crear, listar, actualizar y eliminar metas individuales.
    Calcula progreso y dispara notificaciones automáticamente.
    """
    serializer_class = FinancialGoalSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrReadOnly]

    def get_queryset(self):
        return FinancialGoal.objects.filter(user=self.request.user).order_by('-month', 'name')

    def perform_create(self, serializer):
        goal = serializer.save(user=self.request.user, current_amount=0)
        self.update_goal_progress(goal)

    def perform_update(self, serializer):
        goal = serializer.save()
        self.update_goal_progress(goal)

    def update_goal_progress(self, goal):
        """
        Calcula el progreso de la meta sumando todos los ingresos menos gastos
        del mes de la meta. Actualiza 'current_amount', 'progress' y dispara
        notificación si se alcanza la meta.
        """
        user = goal.user
        month = goal.month

        total_income = user.transactions.filter(
            category__type='income',
            date__year=month.year,
            date__month=month.month
        ).aggregate(total=Sum('amount'))['total'] or 0

        total_expense = user.transactions.filter(
            category__type='expense',
            date__year=month.year,
            date__month=month.month
        ).aggregate(total=Sum('amount'))['total'] or 0

        current_savings = total_income - total_expense
        goal.current_amount = current_savings
        goal.progress = round((current_savings / goal.target_amount) * 100, 2) if goal.target_amount else 0

        if current_savings >= goal.target_amount and not goal.achieved:
            goal.achieved = True
            NotificationService.create(
                user=user,
                type='GOAL_COMPLETED',
                title=f"Meta alcanzada: {goal.name}",
                message=f"¡Felicidades! Has alcanzado tu meta '{goal.name}' de ${goal.target_amount:.2f}.",
                priority='MEDIUM',
                send_email=True
            )

        goal.save()


    # ==========================================================
    # Acción para agregar un aporte parcial a la meta
    # ==========================================================
    @action(detail=True, methods=['post'], url_path='add-amount')
    def add_amount(self, request, pk=None):
        goal = self.get_object()
        amount = request.data.get('amount')
        try:
            amount = float(amount)
        except (TypeError, ValueError):
            return Response({"error": "Monto inválido"}, status=status.HTTP_400_BAD_REQUEST)

        goal.current_amount += amount
        self.update_goal_status(goal)
        goal.save()

        serializer = self.get_serializer(goal)
        return success_response(data=serializer.data, message=f"Aporte de ${amount:.2f} agregado correctamente")

    # ==========================================================
    # Obtener progreso de una meta
    # ==========================================================
    @action(detail=True, methods=['get'], url_path='progress')
    def progress(self, request, pk=None):
        """
        Retorna el porcentaje alcanzado de la meta.
        """
        goal = self.get_object()
        month = goal.month
        user = request.user

        total_income = user.transactions.filter(
            category__type='income',
            date__year=month.year,
            date__month=month.month
        ).aggregate(Sum('amount'))['amount__sum'] or 0

        total_expense = user.transactions.filter(
            category__type='expense',
            date__year=month.year,
            date__month=month.month
        ).aggregate(Sum('amount'))['amount__sum'] or 0

        savings = total_income - total_expense
        percentage = round(min(savings / goal.target_amount * 100, 100), 2) if goal.target_amount else 0

        return success_response(
            data={
                'goal_id': goal.id,
                'name': goal.name,
                'target_amount': float(goal.target_amount),
                'achieved': goal.achieved,
                'current_savings': float(savings),
                'progress_percentage': percentage
            },
            message="Progreso de meta obtenido correctamente."
        )

    # ==========================================================
    # Exportar metas a CSV / Excel
    # ==========================================================
    @action(detail=False, methods=['get'], url_path='export')
    def export(self, request):
        user = request.user
        formato = request.query_params.get('format', 'csv').lower()
        queryset = self.get_queryset()

        if not queryset.exists():
            return error_response("No hay metas para exportar.", status.HTTP_404_NOT_FOUND)

        if formato == 'csv':
            buffer = io.StringIO()
            writer = csv.writer(buffer)
            writer.writerow(["Nombre", "Mes", "Monto objetivo", "Alcanzada"])
            for g in queryset:
                writer.writerow([g.name, g.month.strftime("%Y-%m"), float(g.target_amount), g.achieved])
            response = HttpResponse(buffer.getvalue(), content_type='text/csv')
            response['Content-Disposition'] = f'attachment; filename="metas_{user.username}.csv"'
            return response

        elif formato == 'xlsx':
            wb = Workbook()
            ws = wb.active
            ws.title = "Metas"
            ws.append(["Nombre", "Mes", "Monto objetivo", "Alcanzada"])
            for g in queryset:
                ws.append([g.name, g.month.strftime("%Y-%m"), float(g.target_amount), g.achieved])
            buffer = io.BytesIO()
            wb.save(buffer)
            buffer.seek(0)
            response = HttpResponse(
                buffer.getvalue(),
                content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            )
            response['Content-Disposition'] = f'attachment; filename="metas_{user.username}.xlsx"'
            return response

        return error_response("Formato no soportado. Usa 'csv' o 'xlsx'.", status.HTTP_400_BAD_REQUEST)


# ==========================================================
# NOTIFICACIONES
# ==========================================================
class NotificationViewSet(viewsets.ModelViewSet):
    """
    Vista para gestionar las notificaciones del sistema financiero.
    
    Incluye:
    - Listado y filtrado avanzado (por tipo, prioridad, estado o rango de fechas).
    - Acciones rápidas para marcar como leídas, archivar o limpiar.
    - Envío de correos automáticos o manuales de notificación.
    - Integración completa con NotificationService.
    """
    serializer_class = NotificationSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]

    filterset_fields = ['type', 'priority', 'is_read', 'is_archived']
    search_fields = ['title', 'message']
    ordering_fields = ['created_at', 'priority']
    ordering = ['-created_at']

    def get_queryset(self):
        """
        Devuelve las notificaciones del usuario autenticado.
        Permite filtrado adicional por rango de fechas (start_date, end_date).
        """
        user = self.request.user
        queryset = Notification.objects.filter(user=user).order_by('-created_at')

        start_date = self.request.query_params.get('start_date')
        end_date = self.request.query_params.get('end_date')

        if start_date:
            queryset = queryset.filter(created_at__gte=parse_date(start_date))
        if end_date:
            queryset = queryset.filter(created_at__lte=parse_date(end_date))

        return queryset

    def perform_create(self, serializer):
        """
        Crea una notificación directamente desde la API si fuera necesario.
        (Normalmente las notificaciones se crean mediante NotificationService).
        """
        notification = serializer.save(user=self.request.user)
        user_settings = UserSettings.objects.filter(user=self.request.user).first()

        if user_settings and user_settings.receive_email_notifications:
            send_notification_email(
                to_email=self.request.user.email,
                subject=f"Nueva notificación: {notification.title}",
                message=notification.message
            )

    # ==========================================================
    # ACCIONES PERSONALIZADAS
    # ==========================================================

    @action(detail=True, methods=['post'], url_path='mark-read')
    def mark_read(self, request, pk=None):
        """
        Marca una notificación específica como leída.
        """
        notification = self.get_object()
        if not notification.is_read:
            notification.is_read = True
            notification.save()
        return success_response(message="Notificación marcada como leída.")

    @action(detail=False, methods=['post'], url_path='mark-all-read')
    def mark_all_read(self, request):
        """
        Marca todas las notificaciones del usuario como leídas.
        """
        updated = Notification.objects.filter(user=request.user, is_read=False).update(is_read=True)
        return success_response(message=f"{updated} notificaciones marcadas como leídas.")

    @action(detail=True, methods=['post'], url_path='archive')
    def archive(self, request, pk=None):
        """
        Archiva una notificación específica.
        """
        notification = self.get_object()
        notification.is_archived = True
        notification.save()
        return success_response(message="Notificación archivada correctamente.")

    @action(detail=False, methods=['post'], url_path='clear-read')
    def clear_read(self, request):
        """
        Elimina todas las notificaciones leídas y archivadas del usuario.
        """
        deleted, _ = Notification.objects.filter(
            user=request.user, is_read=True, is_archived=True
        ).delete()
        return success_response(message=f"{deleted} notificaciones eliminadas correctamente.")

    @action(detail=False, methods=['post'], url_path='send-test-email')
    def send_test_email(self, request):
        """
        Envía un correo de prueba de notificación al usuario autenticado.
        Útil para verificar configuración de correo y plantillas.
        """
        user = request.user
        send_notification_email(
            to_email=user.email,
            subject="Prueba de notificación",
            message="Este es un mensaje de prueba del sistema de notificaciones."
        )
        return success_response(message="Correo de prueba enviado correctamente.")

    @action(detail=False, methods=['get'], url_path='summary')
    def summary(self, request):
        """
        Devuelve estadísticas generales de notificaciones del usuario:
        - Total
        - Leídas
        - No leídas
        - Archivadas
        """
        user = request.user
        total = Notification.objects.filter(user=user).count()
        read = Notification.objects.filter(user=user, is_read=True).count()
        unread = Notification.objects.filter(user=user, is_read=False).count()
        archived = Notification.objects.filter(user=user, is_archived=True).count()

        data = {
            "total": total,
            "read": read,
            "unread": unread,
            "archived": archived,
            "percentage_read": round((read / total * 100), 2) if total > 0 else 0
        }
        return success_response(data=data, message="Resumen de notificaciones obtenido correctamente.")


# ==========================================================
# CONFIGURACIÓN DEL USUARIO
# ==========================================================
class UserSettingsViewSet(viewsets.ModelViewSet):
    """
    Vista para gestionar la configuración de notificaciones y preferencias del usuario.
    """
    serializer_class = UserSettingsSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return UserSettings.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
