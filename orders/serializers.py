from django.db import transaction

from rest_framework import serializers

from .models import Order, OrderItem


class OrderItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderItem
        fields = ["order", "product", "quantity", "price",]
        read_only_fields = ["price",]


class OrderSerializer(serializers.ModelSerializer):
    order_items = OrderItemSerializer(many=True)

    class Meta:
        model = Order 
        fields = ["created_by", "status", "total_price", "order_items",]
        read_only_fields = ["total_price",]

    @transaction.atomic 
    def create(self, validated_data):
        order_items_data = validated_data.pop("order_items")

        order = Order.objects.create(
            **validated_data,
            total_price=0
        )

        total_price = 0

        for order_item_data in order_items_data:
            product = order_item_data["product"]
            quantity = order_item_data["quantity"]
            order_item_price = product.price

            OrderItem.objects.create(
                order=order,
                product=product,
                quantity=quantity,
                price=order_item_price
            )

            total_price += order_item_price * quantity 

        order.total_price = total_price
        order.save()

        return order