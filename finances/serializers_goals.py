from rest_framework import serializers
from .models import FinancialGoal
from django.db.models import Sum

class FinancialGoalSerializer(serializers.ModelSerializer):
    progress = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = FinancialGoal
        fields = ['id', 'name', 'user', 'month', 'target_amount', 'current_amount', 'achieved', 'progress', 'created_at']
        read_only_fields = ['id', 'user', 'achieved', 'progress', 'created_at']

    def get_progress(self, obj):
        if obj.target_amount == 0:
            return 0
        return round((obj.current_amount / obj.target_amount) * 100, 2)

    def update(self, instance, validated_data):
        # Si se envía un aporte parcial, sumarlo al monto actual
        additional = validated_data.get('current_amount', 0)
        instance.current_amount += additional

        # Actualizar target_amount si se envía
        instance.target_amount = validated_data.get('target_amount', instance.target_amount)

        # Verificar si la meta se alcanzó
        if instance.current_amount >= instance.target_amount:
            instance.achieved = True

        instance.save()
        return instance
