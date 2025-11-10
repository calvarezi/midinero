from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.conf import settings
from django.db.models import Sum
from decimal import Decimal


class Category(models.Model):
    TYPE_CHOICES = [
        ('income', 'Ingreso'),
        ('expense', 'Gasto'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='categories')
    name = models.CharField(max_length=100, db_index=True)
    type = models.CharField(max_length=10, choices=TYPE_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['name']
        unique_together = ('user', 'name', 'type')
        verbose_name = "Categoría"
        verbose_name_plural = "Categorías"

    def __str__(self):
        return f"{self.name} ({self.get_type_display()})"


class Transaction(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='transactions')
    category = models.ForeignKey(Category, on_delete=models.PROTECT, related_name='transactions')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.CharField(max_length=255, blank=True)
    date = models.DateTimeField(default=timezone.now)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-date']
        verbose_name = "Transacción"
        verbose_name_plural = "Transacciones"

    @property
    def is_income(self):
        return self.category.type == 'income'

    @property
    def is_expense(self):
        return self.category.type == 'expense'

    def __str__(self):
        return f"{self.category.name}: {self.amount}"


class FinancialGoal(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='financial_goals')
    name = models.CharField(max_length=255, default="Meta")
    month = models.DateField()
    target_amount = models.DecimalField(max_digits=12, decimal_places=2)
    current_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    achieved = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'name', 'month')
        ordering = ['-month', 'name']

    def __str__(self):
        return f"{self.name} ({self.month.strftime('%Y-%m')})"

    @property
    def progress(self):
        if not self.target_amount:
            return 0
        progress = (self.current_amount / self.target_amount) * 100
        return round(min(progress, 100), 2)



class Notification(models.Model):
    class NotificationType(models.TextChoices):
        HIGH_EXPENSE = 'HIGH_EXPENSE', 'Gasto alto'
        GOAL_COMPLETED = 'GOAL_COMPLETED', 'Meta cumplida'
        BUDGET_EXCEEDED = 'BUDGET_EXCEEDED', 'Presupuesto superado'
        BUDGET_WARNING = 'BUDGET_WARNING', 'Advertencia de presupuesto'  # ✅ AGREGADO
        REMINDER = 'REMINDER', 'Recordatorio'
        SYSTEM = 'SYSTEM', 'Sistema'

    class Priority(models.TextChoices):
        LOW = 'LOW', 'Baja'
        MEDIUM = 'MEDIUM', 'Media'
        HIGH = 'HIGH', 'Alta'

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='notifications')
    type = models.CharField(max_length=32, choices=NotificationType.choices, default=NotificationType.SYSTEM)
    title = models.CharField(max_length=100)
    message = models.TextField()
    priority = models.CharField(max_length=10, choices=Priority.choices, default=Priority.MEDIUM)
    is_read = models.BooleanField(default=False)
    is_archived = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        unique_together = ('user', 'title', 'message')


    def __str__(self):
        return f"[{self.get_type_display()}] {self.title}"


class UserSettings(models.Model):
    """Configuraciones personalizadas del usuario (umbral de gasto, alertas, etc)."""
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="settings")
    high_expense_threshold = models.DecimalField(max_digits=12, decimal_places=2, default=500000)
    receive_email_notifications = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True) 
    
    def __str__(self):
        return f"Configuración de {self.user.username}"


class Budget(models.Model):
    """
    Presupuesto mensual por usuario y categoría.
    month: fecha que indica el mes (usamos el primer día del mes).
    category: FK a Category (presupuesto por categoría).
    limit_amount: monto límite para el mes.
    notify_when_exceeded: si se debe notificar al usuario cuando se supere.
    created_at: fecha de creación.
    """
    user = models.ForeignKey('auth.User', on_delete=models.CASCADE, related_name='budgets')
    category = models.ForeignKey('finances.Category', on_delete=models.CASCADE, related_name='budgets')
    month = models.DateField()
    limit_amount = models.DecimalField(max_digits=12, decimal_places=2)
    notify_when_exceeded = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    @property
    def spent_amount(self):
        total = Transaction.objects.filter(
            user=self.user,
            category=self.category,
            date__year=self.month.year,
            date__month=self.month.month,
        ).aggregate(total=Sum('amount'))['total'] or Decimal('0')
        return round(total, 2)

    def check_status(self):
        """
        ✅ Evita notificaciones duplicadas y calcula progreso en una sola función.
        """
        total_spent = self.spent_amount
        if self.limit_amount == 0:
            return

        progress = (Decimal(total_spent) / Decimal(self.limit_amount)) * Decimal(100)

        # Evita duplicación
        existing = Notification.objects.filter(
            user=self.user,
            title__icontains=self.category.name,
            type__in=['BUDGET_EXCEEDED', 'BUDGET_WARNING'],
            created_at__year=self.month.year,
            created_at__month=self.month.month
        )

        # Si ya hay notificación de este mes, no la duplicamos
        if existing.exists():
            return

        from finances.services.notifications_service import NotificationService

        if progress >= 100 and self.notify_when_exceeded:
            NotificationService.create(
                user=self.user,
                type='BUDGET_EXCEEDED',
                title=f"Presupuesto superado: {self.category.name}",
                message=(
                    f"Has superado el presupuesto de ${self.limit_amount:.2f} "
                    f"para {self.category.name}. Gasto total: ${total_spent:.2f}."
                ),
                priority='HIGH',
                send_email=True
            )

        elif progress >= 90 and self.notify_when_exceeded:
            NotificationService.create(
                user=self.user,
                type='BUDGET_WARNING',
                title=f"Presupuesto casi agotado: {self.category.name}",
                message=(
                    f"Ya usaste el {progress:.1f}% del presupuesto para {self.category.name} "
                    f"en {self.month.strftime('%Y-%m')}."
                ),
                priority='MEDIUM',
                send_email=True
            )