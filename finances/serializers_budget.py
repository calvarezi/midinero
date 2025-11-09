from rest_framework import serializers
from django.db import models  
from finances.models import Budget, Transaction


class BudgetSerializer(serializers.ModelSerializer):
    spent_amount = serializers.SerializerMethodField(read_only=True)
    progress_percentage = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Budget
        fields = [
            'id',
            'user',
            'category',
            'month',
            'limit_amount',
            'notify_when_exceeded',
            'spent_amount',
            'progress_percentage',
            'created_at',
        ]
        read_only_fields = ['id', 'user', 'spent_amount', 'progress_percentage', 'created_at']

    def get_spent_amount(self, obj):
        """Calcula cuánto se ha gastado en esta categoría/mes."""
        # Usar models.Sum correctamente
        total = Transaction.objects.filter(
            user=obj.user,
            category=obj.category,
            category__type='expense',
            date__year=obj.month.year,
            date__month=obj.month.month
        ).aggregate(total=models.Sum('amount'))['total'] or 0
        return round(float(total), 2)  # ✅ Convertir a float para JSON

    def get_progress_percentage(self, obj):
        """Calcula el porcentaje de progreso del presupuesto."""
        spent = self.get_spent_amount(obj)
        if obj.limit_amount == 0:
            return 0
        # Convertir a float para cálculo
        return round((spent / float(obj.limit_amount)) * 100, 2)

    def create(self, validated_data):
        """Asigna automáticamente el usuario autenticado."""
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)

    def validate_limit_amount(self, value):
        """Valida que el límite del presupuesto sea positivo."""
        if value <= 0:
            raise serializers.ValidationError("El límite del presupuesto debe ser mayor a 0.")
        return value

    def validate(self, attrs):
        """Valida que no exista un presupuesto duplicado para el mismo mes y categoría."""
        user = self.context['request'].user
        month = attrs.get('month')
        category = attrs.get('category')

        # Solo validar en creación, no en actualización
        if not self.instance:
            existing = Budget.objects.filter(
                user=user,
                category=category,
                month=month
            ).exists()

            if existing:
                raise serializers.ValidationError(
                    "Ya existe un presupuesto para esta categoría en este mes."
                )

        return attrs