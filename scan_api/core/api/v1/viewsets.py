from django.db.models import Count, Q
from rest_framework import viewsets

from core.api.v1.serializers import ClassGroupSerializer, StudentSerializer
from core.models import ClassGroup, Student


class ClassGroupViewSet(viewsets.ModelViewSet):
    serializer_class = ClassGroupSerializer

    def get_queryset(self):
        return (
            ClassGroup.active
            .filter(owner=self.request.user)
            .annotate(
                students_count=Count(
                    "students",
                    filter=Q(students__is_deleted=False),
                )
            )
        )

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)


class StudentViewSet(viewsets.ModelViewSet):
    serializer_class = StudentSerializer

    def get_queryset(self):
        queryset = (
            Student.active
            .filter(class_group__owner=self.request.user)
            .select_related("class_group")
        )

        class_group = self.request.query_params.get("class_group")
        if class_group:
            queryset = queryset.filter(class_group_id=class_group)

        return queryset
