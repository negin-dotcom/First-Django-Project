from django.db import models 
from django.contrib.auth.models import User

from products.models import Product


class Order(models.Model):
    class Status(models.TextChoices):
        PENDING = "PENDING"
        PAID = "PAID"
        SHIPPED = "SHIPPED"
        COMPLETED = "COMPLETED"
        CANCELLED = "CANCELLED"
    
    created_by = models.ForeignKey(User,
                                   related_name="orders",
                                   on_delete=models.PROTECT)

    created_at = models.DateTimeField(auto_now_add=True)

    status = models.CharField(max_length=20,
                              choices=Status.choices,
                              default=Status.PENDING)

    total_price = models.DecimalField(max_digits=10,
                                      decimal_places=2)


class OrderItem(models.Model):        
    order = models.ForeignKey(Order,
                              related_name="order_items",
                              on_delete=models.PROTECT)

    product = models.ForeignKey(Product,
                                related_name="order_items",
                                on_delete=models.PROTECT)

    quantity = models.IntegerField()

    price = models.DecimalField(max_digits=10,
                                 decimal_places=2)

    class Meta:
        constraints = [
            models.CheckConstraint(
                        condition=models.Q(quantity__gte=1),
                        name="quantity_gte_1"
                        ),
            
            models.UniqueConstraint(
                fields=["order", "product"],
                name="unique_order_product"
                ),
        ]