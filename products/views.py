from django.shortcuts import get_object_or_404

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status 

from drf_spectacular.utils import extend_schema

from .models import Category, Product
from .serializers import CategorySerializer, ProductSerializer



class CategoryListCreateView(APIView):
    def get(self, request):
        categories = Category.objects.all()
        serializer = CategorySerializer(categories, many=True)

        return Response(serializer.data)


    def post(self, request):
        serializer = CategorySerializer(data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response(
                serializer.data,
                status=status.HTTP_201_CREATED
            )

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )



class ProductListCreateView(APIView):
    def get(self, request):
        products = Product.objects.all()
        serializer = ProductSerializer(products, many=True)

        return Response(
            serializer.data
        )

    @extend_schema(
        request=ProductSerializer,
        responses=ProductSerializer
    )
    def post(self, request):
        serializer = ProductSerializer(data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response(
                serializer.data,

                status=status.HTTP_201_CREATED
            )
        
        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )


class ProductDetailView(APIView):
    def get(self, request, pk):
        product = get_object_or_404(Product, pk=pk)
        serializer = ProductSerializer(product)

        return Response(
            serializer.data
        )

    @extend_schema(
        request=ProductSerializer,
        responses=ProductSerializer
    )
    def put(self, request, pk):
        product = get_object_or_404(Product, pk=pk)
        serializer = ProductSerializer(product,
                                       data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response(
                serializer.data
            )

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )
    
    @extend_schema(
        request=ProductSerializer,
        responses=ProductSerializer
    )
    def patch(self, request, pk):
            product = get_object_or_404(Product, pk=pk)
            serializer = ProductSerializer(product,
                                           data=request.data,
                                           partial=True)
    
            if serializer.is_valid():
                serializer.save()
                return Response(
                    serializer.data
                )
    
            return Response(
                serializer.errors,
                status=status.HTTP_400_BAD_REQUEST
            )

    def delete(self, request, pk):
        product = get_object_or_404(Product, pk=pk)

        product.delete()

        return Response(
            status=status.HTTP_204_NO_CONTENT
        )