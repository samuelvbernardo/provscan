from rest_framework.routers import DefaultRouter

from accounts.api.v1.viewsets import UserViewSet

router = DefaultRouter()

router.register(r"users", UserViewSet, basename="user")

urlpatterns = router.urls
