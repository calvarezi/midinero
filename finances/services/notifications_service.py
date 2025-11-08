from django.utils import timezone
from finances.models import Notification, Transaction, FinancialGoal, Budget
from finances.utils.email_utils import send_notification_email


class NotificationService:
    """
    Servicio centralizado para gestionar las notificaciones del sistema MiDinero.
    Se utiliza para notificar eventos importantes:
    - Nuevas transacciones (ingresos o gastos)
    - Metas financieras alcanzadas
    - Presupuestos excedidos
    """

    # ==========================================================
    # MÉTODO BASE DE CREACIÓN DE NOTIFICACIONES
    # ==========================================================
    @staticmethod
    def create(user, type, title, message, priority="NORMAL", send_email=False):
        """
        Crea una notificación en la base de datos y opcionalmente envía un correo.

        Parámetros:
        - user: Usuario destino (instancia)
        - type: tipo de notificación ('TRANSACTION', 'BUDGET_ALERT', 'GOAL_COMPLETED', etc.)
        - title: título visible de la notificación
        - message: cuerpo del mensaje
        - priority: nivel de prioridad ('LOW', 'NORMAL', 'HIGH')
        - send_email: bool → si True, se envía correo al usuario
        """

        notification = Notification.objects.create(
            user=user,
            type=type,
            title=title,
            message=message,
            priority=priority,
            created_at=timezone.now(),
            is_read=False,
            is_archived=False,
        )

        if send_email and user.email:
            try:
                send_notification_email(
                    to_email=user.email,
                    subject=f"[MiDinero] {title}",
                    message=message,
                )
            except Exception as e:
                print(f"⚠️ Error al enviar correo: {e}")

        return notification

    # ==========================================================
    # NOTIFICACIONES DE TRANSACCIONES
    # ==========================================================
    @staticmethod
    def create_transaction_notification(transaction: Transaction, send_email=True):
        """
        Crea una notificación automáticamente al registrar una transacción.

        Envía una alerta dependiendo del tipo:
        - Si es ingreso → mensaje positivo
        - Si es gasto alto → alerta
        """
        user = transaction.user
        category_type = transaction.category.type
        amount = transaction.amount

        if category_type == "income":
            title = "Ingreso registrado"
            message = f"Has registrado un ingreso de ${amount:,.2f} en la categoría '{transaction.category.name}'."
            priority = "NORMAL"
        else:
            title = "Gasto registrado"
            message = f"Has registrado un gasto de ${amount:,.2f} en '{transaction.category.name}'."
            priority = "NORMAL"

            # Alerta si gasto supera un umbral configurable
            if amount >= 500000:  # puedes ajustar el umbral o hacerlo configurable
                title = "⚠️ Gasto Alto Detectado"
                message = f"Tu gasto de ${amount:,.2f} en '{transaction.category.name}' supera el límite recomendado."
                priority = "HIGH"

        return NotificationService.create(
            user=user,
            type="TRANSACTION",
            title=title,
            message=message,
            priority=priority,
            send_email=send_email,
        )

    # ==========================================================
    # NOTIFICACIONES DE METAS FINANCIERAS
    # ==========================================================
    @staticmethod
    def create_goal_notification(goal: FinancialGoal, reached=False):
        """
        Notifica al usuario sobre el progreso o cumplimiento de una meta.
        """
        user = goal.user
        if reached:
            title = "🎯 ¡Meta Financiera Alcanzada!"
            message = f"Has alcanzado tu meta '{goal.name}' de ${goal.target_amount:,.2f}."
            priority = "HIGH"
        else:
            title = "Progreso en tu meta"
            message = f"Tu meta '{goal.name}' lleva un avance del {goal.progress_percentage()}%."
            priority = "NORMAL"

        return NotificationService.create(
            user=user,
            type="GOAL",
            title=title,
            message=message,
            priority=priority,
            send_email=True,
        )

    # ==========================================================
    # NOTIFICACIONES DE PRESUPUESTOS
    # ==========================================================
    @staticmethod
    def create_budget_notification(budget: Budget, exceeded=False):
        """
        Notifica al usuario si el presupuesto fue excedido o actualizado.
        """
        user = budget.user
        if exceeded:
            title = "🚨 Presupuesto Excedido"
            message = f"Has superado tu presupuesto '{budget.name}' de ${budget.limit_amount:,.2f}."
            priority = "HIGH"
        else:
            title = "Presupuesto actualizado"
            message = f"Se actualizó tu presupuesto '{budget.name}'."
            priority = "NORMAL"

        return NotificationService.create(
            user=user,
            type="BUDGET",
            title=title,
            message=message,
            priority=priority,
            send_email=True,
        )

    # ==========================================================
    # MÉTODOS DE GESTIÓN DE NOTIFICACIONES
    # ==========================================================
    @staticmethod
    def mark_as_read(notification_id, user):
        """Marca una notificación como leída."""
        try:
            notif = Notification.objects.get(id=notification_id, user=user)
            notif.is_read = True
            notif.save()
            return True
        except Notification.DoesNotExist:
            return False

    @staticmethod
    def mark_all_as_read(user):
        """Marca todas las notificaciones del usuario como leídas."""
        Notification.objects.filter(user=user, is_read=False).update(is_read=True)

    @staticmethod
    def archive(notification_id, user):
        """Archiva una notificación específica."""
        try:
            notif = Notification.objects.get(id=notification_id, user=user)
            notif.is_archived = True
            notif.save()
            return True
        except Notification.DoesNotExist:
            return False

    @staticmethod
    def clear_archived(user):
        """Elimina las notificaciones archivadas."""
        Notification.objects.filter(user=user, is_archived=True).delete()
