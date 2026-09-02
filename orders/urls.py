from django.urls import path

from .views import (
    OrderListCreateView,
    OrderDetailView,
    OrderItemListCreateView,
    OrderItemDetailView
)


urlpatterns = [
     path("orders/",
          OrderListCreateView.as_view(),
          name="orders"),

     path("orders/<int:pk>/",
          OrderDetailView.as_view(),
          name="order"),

     path("order-items/",
          OrderItemListCreateView.as_view(),
          name="order_items"),

     path("order-items/<int:pk>/",
          OrderItemDetailView.as_view(),
          name="order_item"),
]