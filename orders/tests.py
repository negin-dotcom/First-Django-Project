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

    def test_user_cannot_access_other_users_order_item(self):
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
            user=self.user_2
        )

        response = self.client.get(f"/api/order-items/{user_order_item.id}/")

        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN
        )

    def test_user_can_access_own_order_items(self):
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

        product_category_2 = Category.objects.create(
            name="test_category_2"
        )

        user_product_2 = Product.objects.create(
            name="test_product_2",
            description="this is a test_product_2.",
            price=Decimal("170.0"),
            stock=6,
            category=product_category_2
        )

        user_order_2 = Order.objects.create(
            created_by=self.user_2,
            status=Order.Status.SHIPPED,
            total_price=Decimal("190.0")
        )

        user_order_item_2 = OrderItem.objects.create(
            order=user_order_2,
            product=user_product_2,
            quantity=1,
            price=Decimal(user_product_2.price)
        )

        self.client.force_authenticate(
            user=self.user
        )

        response = self.client.get(f"/api/order-items/")
        
        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK
        )

        returned_orders = [order["order"] for order in response.data]

        self.assertIn(
            user_order.id, returned_orders
        )

        self.assertNotIn(
            user_order_2.id, returned_orders
        )

    def test_authenticated_user_can_create_order(self):
        product_category = Category.objects.create(
            name="test_category"
        )

        product = Product.objects.create(
            name="test_product",
            description="this is test_product.",
            price=Decimal("110.00"),
            stock=5,
            category=product_category
        )

        self.client.force_authenticate(
            user=self.user
        )

        data = {
            "order_items_data": [
                {
                    "product": product.id,
                    "quantity": 1,
                }
            ]
        }

        response = self.client.post("/api/orders/",
                                    data=data,
                                    format="json")

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED
        )

    def test_unauthenticated_user_cannot_create_order(self):
        product_category = Category.objects.create(
            name="test_category"
        )
        
        product = Product.objects.create(
            name="test_product",
            description="this is test_product.",
            price=Decimal("110.00"),
            stock=5,
            category=product_category
        )

        data = {
            "order_items_data": [
                {
                    "product": product.id,
                    "quantity": 1,
                }
            ]
        }

        response = self.client.post("/api/orders/",
                                    data=data,
                                    format="json")

        self.assertEqual(
            response.status_code,
            status.HTTP_401_UNAUTHORIZED
        )

    def test_create_order_with_insufficient_stock(self):
        product_category = Category.objects.create(
            name="test_category"
        )

        product = Product.objects.create(
            name="test_product",
            description="this is a test product.",
            price=Decimal("110.00"),
            stock=2,
            category=product_category
        )

        self.client.force_authenticate(
            user=self.user
        )

        data = {
            "order_items_data": [
                {
                    "product": product.id,
                    "quantity": 3,
                }
            ]
        }

        response = self.client.post("/api/orders/",
                                    data=data,
                                    format="json")

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST
        )

        product.refresh_from_db()
        self.assertEqual(
            product.stock,
            2
        )

        self.assertEqual(
            Order.objects.count(),
            0
        )

        self.assertEqual(
            OrderItem.objects.count(),
            0
        )

    def test_create_order_with_nonexistent_product(self):     
        self.client.force_authenticate(
            user=self.user
        )

        data = {
            "order_items_data": [
                {
                    "product": Product.objects.count() + 1,
                    "quantity": 1,
                }
            ]
        }

        response = self.client.post("/api/orders/",
                                    data=data,
                                    format="json")


        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST
        )

    def test_create_order_with_invalid_quantity(self):
        product_category = Category.objects.create(
                name="test_category"
        )

        product = Product.objects.create(
            name="test_product",
            description="this is a test product.",
            price=Decimal("110.00"),
            stock=2,
            category=product_category
        )
         
        self.client.force_authenticate(
            user=self.user
        )

        data = {
            "order_items_data": [
                {
                    "product": product.id,
                    "quantity": 0,
                }
            ]
        }

        response = self.client.post("/api/orders/",
                                    data=data,
                                    format="json")


        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST
        )

    def test_create_order_reduces_product_stock(self):
        product_category = Category.objects.create(
                name="test_category"
        )

        product = Product.objects.create(
            name="test_product",
            description="this is a test product.",
            price=Decimal("110.00"),
            stock=5,
            category=product_category
        )

        self.client.force_authenticate(
            user=self.user
        )

        data = {
            "order_items_data": [
                {
                    "product": product.id,
                    "quantity": 2,
                }
            ]
        }

        response = self.client.post("/api/orders/",
                                    data=data,
                                    format="json")

        
        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED
        )

        product.refresh_from_db()

        self.assertEqual(
            product.stock,
            3
        )

        order = Order.objects.get(created_by=self.user)
        self.assertEqual(
            order.total_price,
            Decimal("220.00")
        )

    def test_create_order_preserves_product_price(self):
        product_category = Category.objects.create(
                name="test_category"
        )

        product = Product.objects.create(
            name="test_product",
            description="this is a test product.",
            price=Decimal("110.00"),
            stock=5,
            category=product_category
        )

        self.client.force_authenticate(
            user=self.user
        )

        data = {
            "order_items_data": [
                {
                    "product": product.id,
                    "quantity": 2,
                }
            ]
        }

        response = self.client.post("/api/orders/",
                                    data=data,
                                    format="json")

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED
        )
        
        order = Order.objects.get(created_by=self.user)
        order_item = OrderItem.objects.get(order=order)

        self.assertEqual(
            order_item.price,
            Decimal("110.00")
        )

    def test_create_order_with_multiple_products(self):
        product_category = Category.objects.create(
            name="test_category"
        )

        product_1 = Product.objects.create(
            name="product_1",
            price=Decimal("100.0"),
            stock=5,
            category=product_category
        )

        product_2 = Product.objects.create(
            name="product_2",
            price=Decimal("50.0"),
            stock=10,
            category=product_category
        )

        self.client.force_authenticate(
            user=self.user
        )

        data = {
            "order_items_data": [
                {
                    "product": product_1.id,
                    "quantity": 2,
                },
                {
                    "product": product_2.id,
                    "quantity": 3,
                },
            ]
        }

        response = self.client.post("/api/orders/",
                                    data=data,
                                    format="json")

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED
        )

        product_1.refresh_from_db()
        product_2.refresh_from_db()

        self.assertEqual(
            product_1.stock,
            3
        )

        self.assertEqual(
            product_2.stock,
            7
        )

        self.assertEqual(
            OrderItem.objects.count(),
            2
        )

        order = Order.objects.get(created_by=self.user)

        self.assertEqual(
            order.total_price,
            Decimal("100.00") * 2 + Decimal("50.00") * 3
        )

    def test_create_order_with_transaction_rollback(self):
        product_category = Category.objects.create(
            name="test_category"
        )

        product_1 = Product.objects.create(
            name="product_1",
            price=Decimal("100.0"),
            stock=5,
            category=product_category
        )

        product_2 = Product.objects.create(
            name="product_2",
            price=Decimal("50.0"),
            stock=2,
            category=product_category
        )

        self.client.force_authenticate(
            user=self.user
        )

        data = {
            "order_items_data": [
                {
                    "product": product_1.id,
                    "quantity": 2,
                },
                {
                    "product": product_2.id,
                    "quantity": 3,
                },
            ]
        }

        response = self.client.post("/api/orders/",
                                    data=data,
                                    format="json")

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST
        )

        product_1.refresh_from_db()
        product_2.refresh_from_db()

        self.assertEqual(
            product_1.stock,
            5
        )

        self.assertEqual(
            product_2.stock,
            2
        )

        self.assertEqual(
            Order.objects.count(),
            0
        )

        self.assertEqual(
            OrderItem.objects.count(),
            0
        )

    def test_create_order_with_cancellation_restores_stock(self):
        product_category = Category.objects.create(
            name="test_category"
        )

        product = Product.objects.create(
            name="product",
            price=Decimal("100.0"),
            stock=5,
            category=product_category
        )

        self.client.force_authenticate(
            user=self.user
        )

        data = {
            "order_items_data": [
                {
                    "product": product.id,
                    "quantity": 2,
                }
            ]
        }

        response = self.client.post("/api/orders/",
                                    data=data,
                                    format="json")

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED
        )

        product.refresh_from_db()

        self.assertEqual(
            product.stock,
            3
        )

        order = Order.objects.get(created_by=self.user)

        data = {
            "status": Order.Status.CANCELLED
        }

        response = self.client.patch(f"/api/orders/{order.id}/",
                                     data=data,
                                     format="json")

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK
        )

        product.refresh_from_db()

        self.assertEqual(
            product.stock,
            5
        )

        order.refresh_from_db()

        self.assertEqual(
            order.status,
            Order.Status.CANCELLED
        )

    def test_delete_pending_order(self):
        product_category = Category.objects.create(
            name="test_category"
        )

        product = Product.objects.create(
            name="product",
            price=Decimal("100.0"),
            stock=5,
            category=product_category
        )

        self.client.force_authenticate(
            user=self.user
        )

        data = {
            "order_items_data": [
                {
                    "product": product.id,
                    "quantity": 2,
                }
            ]
        }

        response = self.client.post("/api/orders/",
                                    data=data,
                                    format="json")

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED
        )

        order = Order.objects.get(created_by=self.user)

        self.assertEqual(
            order.status,
            Order.Status.PENDING
        )

        response = self.client.delete(f"/api/orders/{order.id}/")

        product.refresh_from_db()

        self.assertEqual(
            response.status_code,
            status.HTTP_204_NO_CONTENT
        )

        self.assertEqual(
            product.stock,
            5
        )

        self.assertEqual(
            Order.objects.count(),
            0
        )

        self.assertEqual(
            OrderItem.objects.count(),
            0
        )

    def test_cannot_delete_non_pending_order(self):
        product_category = Category.objects.create(
            name="test_category"
        )

        product = Product.objects.create(
            name="product",
            price=Decimal("100.0"),
            stock=5,
            category=product_category
        )

        self.client.force_authenticate(
            user=self.user
        )

        data = {
            "order_items_data": [
                {
                    "product": product.id,
                    "quantity": 2,
                }
            ]
        }

        response = self.client.post("/api/orders/",
                                    data=data,
                                    format="json")

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED
        )

        data = {
            "status": Order.Status.PAID
        }

        order = Order.objects.get(created_by=self.user)

        response = self.client.patch(f"/api/orders/{order.id}/",
                                     data=data,
                                     format="json")
        order.refresh_from_db()

        self.assertEqual(
            order.status,
            Order.Status.PAID
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK
        )
    
        response = self.client.delete(f"/api/orders/{order.id}/")

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST
        )

        order.refresh_from_db()
        product.refresh_from_db()

        self.assertEqual(
            Order.objects.count(),
            1
        )

        self.assertEqual(
            product.stock,
            3
        )

    def test_invalid_status_transition(self):
        product_category = Category.objects.create(
            name="test_category"
        )

        product = Product.objects.create(
            name="product",
            price=Decimal("100.0"),
            stock=5,
            category=product_category
        )

        self.client.force_authenticate(
            user=self.user
        )

        data = {
            "order_items_data": [
                {
                    "product": product.id,
                    "quantity": 2,
                }
            ]
        }

        response = self.client.post("/api/orders/",
                                    data=data,
                                    format="json")

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED
        )

        order = Order.objects.get(created_by=self.user)

        data = {
            "status": Order.Status.COMPLETED
        }

        response = self.client.patch(f"/api/orders/{order.id}/",
                                        data=data,
                                        format="json")
    
        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST
        )

        order.refresh_from_db()

        self.assertEqual(
            order.status,
            Order.Status.PENDING
        )