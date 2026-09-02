from django.db import models 


class Category(models.Model):
    name = models.CharField(max_length=100,
                            unique=True)

    class Meta:
        verbose_name = "Category"
        verbose_name_plural = "Categories"



class Product(models.Model):
    name = models.CharField(max_length=100)
    
    description = models.TextField(max_length=200, 
                                   blank=True)

    price = models.DecimalField(max_digits=10,
                                decimal_places=2)

    stock = models.IntegerField()

    category = models.ForeignKey(Category,
                                 related_name="products",
                                 on_delete=models.PROTECT)

    class Meta:
        constraints = [
            models.CheckConstraint(
                condition=models.Q(stock__gte=0),
                name="stock_gte_0"
            ),
        ]