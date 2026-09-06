from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response

from rest_framework import status

from rest_framework.permissions import IsAuthenticated

from drf_spectacular.utils import extend_schema

from .models import Order, OrderItem
from .serializers import OrderSerializer, OrderItemSerializer
from .services import delete_pending_order
from .permissions import IsOrderItemOwner, IsOrderOwner


class OrderListCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        orders = Order.objects.filter(created_by=request.user)
        serializer = OrderSerializer(orders, many=True)

        return Response(
            serializer.data
        )

    @extend_schema(
        request=OrderSerializer,
        responses=OrderSerializer
    )
    def post(self, request):
        serializer = OrderSerializer(data=request.data)

        if serializer.is_valid():
            serializer.save(created_by=request.user)
            return Response(
                serializer.data,
                status=status.HTTP_201_CREATED
            )

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )


class OrderDetailView(APIView):
    permission_classes = [IsAuthenticated, IsOrderOwner]

    def get(self, request, pk):
        order = get_object_or_404(Order, 
                                  pk=pk)

        self.check_object_permissions(request, order)
        
        serializer = OrderSerializer(order)

        return Response(
            serializer.data
        )

    @extend_schema(
        request=OrderSerializer,
        responses=OrderSerializer
    )
    def patch(self, request, pk):
        order = get_object_or_404(Order,
                                  pk=p) 

        self.check_object_permissions(request, order)
        
        serializer = OrderSerializer(order,
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
        order = get_object_or_404(Order, 
                                  pk=pk)

        self.check_object_permissions(request, order)

        try:
            delete_pending_order(order)

        except ValueError as e:
            return Response(
                {"detail": str(e),},
                status=status.HTTP_400_BAD_REQUEST
            )

        return Response(
            status=status.HTTP_204_NO_CONTENT
        )
    

class OrderItemListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        order_items = OrderItem.objects.filter(order__created_by=request.user)

        serializer = OrderItemSerializer(order_items,
                                         many=True)

        return Response(
            serializer.data
        ) 


class OrderItemDetailView(APIView):
    permission_classes = [IsAuthenticated, IsOrderItemOwner]

    def get(self, request, pk):
        order_item = get_object_or_404(OrderItem, 
                                       pk=pk)

        self.check_object_permissions(request, order_item)

        serializer = OrderItemSerializer(order_item) 

        return Response(
            serializer.data
        )

 