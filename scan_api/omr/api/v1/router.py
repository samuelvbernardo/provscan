from rest_framework.routers import DefaultRouter

from omr.api.v1.viewsets import ExamViewSet, OMRViewSet, ScanResultViewSet

router = DefaultRouter()

router.register(r"exams", ExamViewSet, basename="exam")
router.register(r"scan-results", ScanResultViewSet, basename="scan-result")
router.register(r"omr", OMRViewSet, basename="omr")

urlpatterns = router.urls