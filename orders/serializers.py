from django.db import transaction

from rest_framework import serializers

from orders.services import create_order, restore_order_stock, update_order_status
from products.models import Product

from .models import Order, OrderItem


class OrderItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderItem
        fields = ["order", "product", "quantity", "price",]
        read_only_fields = ["order", "price",]


class OrderSerializer(serializers.ModelSerializer):
    order_items = OrderItemSerializer(many=True, 
                                      read_only=True)

    class Meta:
        model = Order 
        fields = ["created_by", "status", "total_price", "order_items",]
        read_only_fields = ["created_by", "total_price",]

    def create(self, validated_data):
        order_items_data = validated_data.pop("order_items")

        return create_order(
            created_by=validated_data["created_by"],
            order_items_data=order_items_data
        )

    def update(self, instance, validated_data):
        new_status = validated_data.get("status")

        if new_status is not None:
            try:
                return update_order_status(
                    order=instance, 
                    new_status=new_status
                )

            except ValueError as e:
                raise serializers.ValidationError(str(e))


        return instance
                