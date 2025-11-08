from django.contrib import admin
from django.utils.html import format_html
from django.db.models import Sum
from .models import Category, Transaction, FinancialGoal, Budget, Notification, UserSettings

# ===========================================================
# ADMIN DE CATEGORÍAS
# ===========================================================
@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'type', 'user', 'created_at', 'transaction_count')
    list_filter = ('type', 'user', 'created_at')
    search_fields = ('name', 'user__username')
    ordering = ('name',)
    readonly_fields = ('created_at',)

    def transaction_count(self, obj):
        return obj.transactions.count()
    transaction_count.short_description = 'Transacciones asociadas'

# ===========================================================
# ADMIN DE TRANSACCIONES
# ===========================================================
@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ('id', 'category', 'formatted_amount', 'user', 'date', 'created_at', 'is_income', 'is_expense')
    list_filter = ('category__type', 'user', 'date', 'created_at')
    search_fields = ('category__name', 'user__username', 'description')
    ordering = ('-date',)
    readonly_fields = ('created_at',)

    def formatted_amount(self, obj):
        try:
            return f"${float(obj.amount):,.2f}"
        except (TypeError, ValueError):
            return obj.amount or "—"
    formatted_amount.short_description = "Monto"

    def is_income(self, obj):
        return obj.category.type == 'income'
    is_income.boolean = True
    is_income.short_description = 'Es Ingreso'

    def is_expense(self, obj):
        return obj.category.type == 'expense'
    is_expense.boolean = True
    is_expense.short_description = 'Es Gasto'

# ===========================================================
# ADMIN DE METAS FINANCIERAS
# ===========================================================
@admin.register(FinancialGoal)
class FinancialGoalAdmin(admin.ModelAdmin):
    list_display = ('user', 'month_display', 'target_amount', 'current_savings', 'progress_percentage', 'achieved', 'created_at')
    list_filter = ('achieved', 'month', 'user')
    search_fields = ('user__username', 'name')
    ordering = ('-month',)
    readonly_fields = ('created_at', 'current_savings', 'progress_percentage', 'month_display')

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user')

    def month_display(self, obj):
        return obj.month.strftime("%Y-%m") if obj.month else None
    month_display.short_description = 'Mes'

    def current_savings(self, obj):
        user = obj.user
        month = obj.month
        total_income = user.transactions.filter(category__type='income', date__year=month.year, date__month=month.month).aggregate(total=Sum('amount'))['total'] or 0
        total_expense = user.transactions.filter(category__type='expense', date__year=month.year, date__month=month.month).aggregate(total=Sum('amount'))['total'] or 0
        return total_income - total_expense
    current_savings.short_description = 'Ahorro actual'

    def progress_percentage(self, obj):
        savings = self.current_savings(obj)
        return round((savings / obj.target_amount) * 100, 2) if obj.target_amount else 0
    progress_percentage.short_description = 'Progreso (%)'

# ===========================================================
# ADMIN DE PRESUPUESTOS
# ===========================================================
@admin.register(Budget)
class BudgetAdmin(admin.ModelAdmin):
    list_display = ('user', 'category', 'month_display', 'limit_amount', 'spent_amount', 'progress_bar', 'notify_when_exceeded', 'created_at')
    list_filter = ('month', 'category', 'user', 'notify_when_exceeded')
    search_fields = ('user__username', 'category__name')
    ordering = ('-month',)
    readonly_fields = ('created_at', 'progress_bar', 'month_display', 'spent_amount')

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user', 'category')

    def month_display(self, obj):
        return obj.month.strftime("%Y-%m") if obj.month else "-"
    month_display.short_description = "Mes"

    def spent_amount(self, obj):
        total = Transaction.objects.filter(user=obj.user, category=obj.category, category__type='expense', date__year=obj.month.year, date__month=obj.month.month).aggregate(total=Sum('amount'))['total'] or 0
        return round(total, 2)
    spent_amount.short_description = "Monto gastado"

    def progress_percentage(self, obj):
        return round((self.spent_amount(obj) / obj.limit_amount) * 100, 2) if obj.limit_amount else 0

    def progress_bar(self, obj):
        progress = self.progress_percentage(obj)
        if progress <= 70:
            color = "#4CAF50"
        elif progress <= 100:
            color = "#FFB300"
        else:
            color = "#E53935"
        return format_html(
            f'<div style="width:120px; border:1px solid #ccc; border-radius:8px;">'
            f'<div style="width:{min(progress, 100)}%; background-color:{color}; height:14px; border-radius:8px;"></div>'
            f'</div>'
            f'<span style="margin-left:8px;">{progress:.1f}%</span>'
        )
    progress_bar.short_description = "Progreso"

    def get_readonly_fields(self, request, obj=None):
        readonly = list(super().get_readonly_fields(request, obj))
        if obj:
            readonly += ['user', 'category', 'month']
        return readonly

# ===========================================================
# ADMIN DE NOTIFICACIONES
# ===========================================================
@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('user', 'type', 'title', 'message_preview', 'is_read', 'created_at')
    list_filter = ('type', 'is_read', 'user')
    search_fields = ('title', 'message', 'user__username')
    ordering = ('-created_at',)
    readonly_fields = ('created_at',)

    def message_preview(self, obj):
        return (obj.message[:60] + '...') if len(obj.message) > 60 else obj.message
    message_preview.short_description = 'Mensaje'

# ===========================================================
# ADMIN DE CONFIGURACIÓN DE USUARIO
# ===========================================================
@admin.register(UserSettings)
class UserSettingsAdmin(admin.ModelAdmin):
    list_display = ('user', 'high_expense_threshold', 'receive_email_notifications', 'created_at')
    list_filter = ('receive_email_notifications',)
    search_fields = ('user__username',)
    ordering = ('-created_at',)
    readonly_fields = ('created_at',)

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user')
