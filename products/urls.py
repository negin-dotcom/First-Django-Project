from django.urls import path 

from .views import CategoryListCreateView, ProductDetailView, ProductListCreateView


urlpatterns = [
    path("categories/",
         CategoryListCreateView.as_view(),
         name="categories"),

    path("products/",
         ProductListCreateView.as_view(),
         name="products"),

     path("products/<int:pk>/",
          ProductDetailView.as_view(),
          name="product"),
]