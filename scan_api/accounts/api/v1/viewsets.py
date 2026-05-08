from django.contrib.auth import get_user_model
from rest_framework import permissions, viewsets

from accounts.api.v1.serializers import UserCreateSerializer, UserSerializer


User = get_user_model()


class IsOwner(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        return request.user.is_staff or obj == request.user


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all().order_by("email")

    def get_serializer_class(self):
        if self.action == "create":
            return UserCreateSerializer
        return UserSerializer

    def get_permissions(self):
        if self.action == "create":
            return [permissions.AllowAny()]
        if self.action in ("list", "destroy"):
            return [permissions.IsAdminUser()]
        return [permissions.IsAuthenticated(), IsOwner()]