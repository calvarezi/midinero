from rest_framework import serializers
from .models import Notification, FinancialGoal

class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = [
            'id',
            'type',
            'title',
            'message',
            'is_read',       
            'is_archived',  
            'priority',
            'created_at',
        ]
        read_only_fields = ['id', 'created_at']


class FinancialGoalSerializer(serializers.ModelSerializer):
    """Serializer de metas de ahorro."""
    class Meta:
        model = FinancialGoal
        fields = ['id', 'month', 'target_amount', 'achieved']
