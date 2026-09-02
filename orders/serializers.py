from rest_framework import serializers

from .models import Order, OrderItem


class OrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order 
        fields = ["created_by", "status", "total_price",]


class OrderItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderItem
        fields = ["order", "product", "quantity", "price",]