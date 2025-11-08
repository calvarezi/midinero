from rest_framework import serializers
from .models import Category, Transaction


class CategorySerializer(serializers.ModelSerializer):
    """
    Serializer para crear y mostrar categorías de ingresos o gastos.
    """

    class Meta:
        model = Category
        exclude = ['user']
        read_only_fields = ['id']
        extra_kwargs = {
            'name': {'required': True},
            'type': {'required': True}
        }
        example = {
            "name": "Alimentación",
            "type": "expense"
        }

    def validate_name(self, value):
        """
        Evita que el usuario cree categorías duplicadas con el mismo nombre.
        """
        user = self.context['request'].user
        if Category.objects.filter(user=user, name__iexact=value).exists():
            raise serializers.ValidationError("Ya existe una categoría con este nombre.")
        return value


from rest_framework import serializers
from .models import Transaction, Category


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name', 'type']


class TransactionSerializer(serializers.ModelSerializer):
    """
    Serializer para transacciones (ingresos y gastos).
    El usuario autenticado se asigna automáticamente.
    """
    category_detail = CategorySerializer(source='category', read_only=True)

    class Meta:
        model = Transaction
        fields = [
            'id',
            'category',
            'category_detail',
            'amount',
            'description',
            'date',
            'created_at'
        ]
        read_only_fields = ['id', 'created_at', 'category_detail']

    def create(self, validated_data):
        """
        Asigna automáticamente el usuario autenticado antes de guardar la transacción.
        """
        user = self.context['request'].user
        validated_data['user'] = user
        return super().create(validated_data)

