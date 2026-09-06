from rest_framework import serializers

from orders.services import create_order, update_order_status

from .models import Order, OrderItem


class OrderItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderItem
        fields = ["order", "product", "quantity", "price",]
        read_only_fields = ["order", "price",]

    def validate_quantity(self, value):
        if value < 1:
            raise serializers.ValidationError(
                "Quantity must be at least 1."
            )

        return value


class OrderSerializer(serializers.ModelSerializer):
    order_items = OrderItemSerializer(many=True, 
                                      read_only=True)
    
    order_items_data = OrderItemSerializer(many=True, 
                                           write_only=True)

    class Meta:
        model = Order 
        fields = ["created_by", "status", "total_price", "order_items",
                  "order_items_data"]
        read_only_fields = ["created_by", "total_price",]

    def create(self, validated_data):
        order_items_data = validated_data.pop("order_items_data")

        try:
            return create_order(
                created_by=validated_data["created_by"],
                order_items_data=order_items_data
            )

        except ValueError as e:
            raise serializers.ValidationError(str(e))

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
                