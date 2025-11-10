from rest_framework import serializers
from finances.models import FinancialGoal
from django.db.models import Sum
from decimal import Decimal



class FinancialGoalSerializer(serializers.ModelSerializer):
    progress = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = FinancialGoal
        fields = "__all__"
        read_only_fields = ['id', 'user', 'achieved', 'progress', 'created_at']

    def get_progress(self, obj):
        """Calcula el porcentaje de progreso de la meta."""
        if obj.target_amount == 0:
            return 0
        return round((float(obj.current_amount) / float(obj.target_amount)) * 100, 2)

    # Lógica de actualización reescrita
    def update(self, instance, validated_data):
        """
        Actualiza la meta financiera.
        
        Comportamientos:
        - Si se envía 'target_amount', se actualiza el objetivo
        - Si se envía 'current_amount', se REEMPLAZA (no suma)
        - Verifica automáticamente si la meta se alcanzó
        """
        # Actualizar campos permitidos
        instance.name = validated_data.get('name', instance.name)
        instance.target_amount = validated_data.get('target_amount', instance.target_amount)
        
        # Reemplazar en vez de sumar
        # Si el usuario quiere agregar un aporte, debe usar la action 'add_amount'
        if 'current_amount' in validated_data:
            instance.current_amount = validated_data['current_amount']

        # Verificar si la meta se alcanzó
        if instance.current_amount >= instance.target_amount:
            instance.achieved = True
            
            # Enviar notificación si es la primera vez que se alcanza
            if not instance.achieved:  # Solo si no estaba marcada como alcanzada antes
                from finances.services.notifications_service import NotificationService
                NotificationService.create(
                    user=instance.user,
                    type='GOAL_COMPLETED',
                    title=f"¡Meta alcanzada: {instance.name}!",
                    message=(
                        f"¡Felicidades! Has alcanzado tu meta '{instance.name}' "
                        f"de ${instance.target_amount:.2f} en {instance.month.strftime('%B %Y')}."
                    ),
                    priority='MEDIUM',
                    send_email=True
                )
        else:
            instance.achieved = False

        instance.save()
        return instance

    def validate_target_amount(self, value):
        """Valida que el monto objetivo sea positivo."""
        if value <= 0:
            raise serializers.ValidationError("El monto objetivo debe ser mayor a 0.")
        return value

    def validate_current_amount(self, value):
        """Valida que el monto actual no sea negativo."""
        if value < 0:
            raise serializers.ValidationError("El monto actual no puede ser negativo.")
        return value

    def validate(self, attrs):
        """Valida que no exista una meta duplicada para el mismo mes y nombre."""
        user = self.context['request'].user
        name = attrs.get('name', self.instance.name if self.instance else None)
        month = attrs.get('month', self.instance.month if self.instance else None)

        # Solo validar en creación, no en actualización del mismo objeto
        if not self.instance or (self.instance.name != name or self.instance.month != month):
            existing = FinancialGoal.objects.filter(
                user=user,
                name=name,
                month=month
            ).exists()

            if existing:
                raise serializers.ValidationError(
                    f"Ya existe una meta con el nombre '{name}' para {month.strftime('%Y-%m')}."
                )

        return attrs


# Serializer para agregar aportes parciales
class AddAmountToGoalSerializer(serializers.Serializer):
    """Serializer para agregar un aporte a una meta existente."""
    amount = serializers.DecimalField(max_digits=12, decimal_places=2, min_value=0.01)

    def validate_amount(self, value):
        """Valida que el aporte sea positivo."""
        if value <= 0:
            raise serializers.ValidationError("El aporte debe ser mayor a 0.")
        return value