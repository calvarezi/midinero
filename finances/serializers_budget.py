from rest_framework import serializers
from finances.models import Budget

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
        from finances.models import Transaction
        total = Transaction.objects.filter(
            user=obj.user,
            category=obj.category,
            category__type='expense',
            date__year=obj.month.year,
            date__month=obj.month.month
        ).aggregate(total=models.Sum('amount'))['total'] or 0
        return round(total, 2)

    def get_progress_percentage(self, obj):
        spent = self.get_spent_amount(obj)
        if obj.limit_amount == 0:
            return 0
        return round((spent / obj.limit_amount) * 100, 2)

    def create(self, validated_data):
        # Asigna automáticamente el usuario autenticado
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)
