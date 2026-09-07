from decimal import Decimal

from django.contrib.auth.models import User

from rest_framework.test import APITestCase
from rest_framework import status

from orders.models import Order, OrderItem
from products.models import Category, Product


class OrderAPITests(APITestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser",
            password="testpass123"
        )

        self.user_2 = User.objects.create_user(
            username="testuser2",
            password="testpass123"
        )

    def test_unauthenticated_user_cannot_get_orders(self):
        response = self.client.get("/api/orders/")

        self.assertEqual(
            response.status_code,
            status.HTTP_401_UNAUTHORIZED
        )

    def test_authenticated_user_can_get_orders(self):
        self.client.force_authenticate(
            user=self.user
        )

        response = self.client.get("/api/orders/")

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK
        )

    def test_user_cannot_access_other_users_order(self):
        user_order = Order.objects.create(
            created_by=self.user,
            status=Order.Status.PENDING,
            total_price=Decimal("120.00")
        )

        self.client.force_authenticate(
            user=self.user_2
        )

        response = self.client.get(f"/api/orders/{user_order.id}/")

        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN
        )

    def test_user_can_access_own_order(self):
        user_order = Order.objects.create(
            created_by=self.user,
            status=Order.Status.PENDING,
            total_price=Decimal("120.00")
        )

        self.client.force_authenticate(
            user=self.user
        )

        response = self.client.get(f"/api/orders/{user_order.id}/")
        
        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK
        )

    def test_user_can_access_own_orders(self):
        user_order = Order.objects.create(
            created_by=self.user,
            status=Order.Status.PENDING,
            total_price=Decimal("120.00")
        )

        user_2_order = Order.objects.create(
            created_by=self.user_2,
            status=Order.Status.SHIPPED,
            total_price=Decimal("140.00")
        )

        self.client.force_authenticate(
            user=self.user
        )

        response = self.client.get("/api/orders/")

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK
        )

        returned_prices = [order["total_price"] for order in response.data]
        
        self.assertIn(
            "120.00", returned_prices
        )

        self.assertNotIn(
            "140.00", returned_prices
        )

    def test_user_can_access_own_order_item(self):
        product_category = Category.objects.create(
            name="test_category"
        )

        user_product = Product.objects.create(
            name="test_product",
            description="this is a test_product.",
            price=Decimal("110.0"),
            stock=5,
            category=product_category
        )

        user_order = Order.objects.create(
            created_by=self.user,
            status=Order.Status.PENDING,
            total_price=Decimal("100.0")
        )

        user_order_item = OrderItem.objects.create(
            order=user_order,
            product=user_product,
            quantity=1,
            price=Decimal(user_product.price)
        )

        self.client.force_authenticate(
            user=self.user
        )

        response = self.client.get(f"/api/order-items/{user_order_item.id}/")

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK
        )
        