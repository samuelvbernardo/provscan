from rest_framework.routers import DefaultRouter

from core.api.v1.viewsets import ClassGroupViewSet, StudentViewSet

router = DefaultRouter()

router.register(r"class-groups", ClassGroupViewSet, basename="class-group")
router.register(r"students", StudentViewSet, basename="student")

urlpatterns = router.urls
