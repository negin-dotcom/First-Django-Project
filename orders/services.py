from django.db import transaction

from orders.models import Order, OrderItem
from products.models import Product 


def restore_order_stock(order):
    order_items = order.order_items.all()

    for order_item in order_items:
        product = Product.objects.select_for_update().get(
            pk=order_item.product.pk
        )

        product.stock += order_item.quantity 
        product.save()


@transaction.atomic 
def create_order(created_by, order_items_data):
    order = Order.objects.create(
        created_by=created_by,
        status=Order.Status.PENDING,
        total_price=0
    )

    total_price = 0

    for order_item_data in order_items_data:
        product = order_item_data["product"]
        quantity = order_item_data["quantity"]

        product = Product.objects.select_for_update().get(
            pk=product.pk
        )

        if product.stock < quantity:
            raise ValueError(
                f"Not enough stock for {product.name}"
            )

        price = product.price

        OrderItem.objects.create(
            order=order,
            product=product,
            quantity=quantity,
            price=price
        )

        product.stock -= quantity
        product.save()

        total_price += price * quantity 

    order.total_price = total_price 
    order.save()

    return order


@transaction.atomic 
def update_order_status(order, new_status):
    old_status = order.status 

    if new_status == old_status:
        return order 

    allowed_transitions = {
        Order.Status.PENDING: [
            Order.Status.PAID,
            Order.Status.CANCELLED,
        ],
        Order.Status.PAID: [
            Order.Status.SHIPPED,
        ],
        Order.Status.SHIPPED: [
            Order.Status.COMPLETED,
        ],
    }

    if new_status not in allowed_transitions.get(old_status, []):
        raise ValueError("Invalid status transition")

    if (
        old_status == Order.Status.PENDING
        and new_status == Order.Status.CANCELLED
    ):
        restore_order_stock(order)

    order.status = new_status 
    order.save()

    return order 

        
@transaction.atomic
def delete_pending_order(order):
    if order.status != order.Status.PENDING:
        raise ValueError(
            "Only pending orders can be deleted."
        )

    restore_order_stock(order)

    order.delete()