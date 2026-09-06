from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response

from rest_framework import status

from .models import Order, OrderItem
from .serializers import OrderSerializer, OrderItemSerializer
from .services import delete_pending_order


class OrderListCreateView(APIView):
    def get(self, request):
        orders = Order.objects.all()
        serializer = OrderSerializer(orders, many=True)

        return Response(
            serializer.data
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
    def get(self, request, pk):
        order = get_object_or_404(Order, pk=pk)
        serializer = OrderSerializer(order)

        return Response(
            serializer.data
        )

    def patch(self, request, pk):
        order = get_object_or_404(Order, pk=pk) 
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
        order = get_object_or_404(Order, pk=pk)

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
    def get(self, request):
        order_items = OrderItem.objects.all()
        serializer = OrderItemSerializer(order_items,
                                         many=True)

        return Response(
            serializer.data
        ) 


class OrderItemDetailView(APIView):
    def get(self, request, pk):
        order_item = get_object_or_404(OrderItem, pk=pk)
        serializer = OrderItemSerializer(order_item) 

        return Response(
            serializer.data
        )

 