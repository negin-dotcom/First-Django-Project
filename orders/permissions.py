from rest_framework.permissions import BasePermission


class IsOrderOwner(BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj.created_by == request.user


class IsOrderItemOwner(BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj.order.created_by == request.user