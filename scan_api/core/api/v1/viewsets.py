from rest_framework import viewsets

from core.api.v1.serializers import ClassGroupSerializer, StudentSerializer
from core.models import ClassGroup, Student


class ClassGroupViewSet(viewsets.ModelViewSet):
    queryset = ClassGroup.active.all()
    serializer_class = ClassGroupSerializer


class StudentViewSet(viewsets.ModelViewSet):
    serializer_class = StudentSerializer

    def get_queryset(self):
        queryset = Student.active.select_related("class_group").all()

        class_group = self.request.query_params.get("class_group")

        if class_group:
            queryset = queryset.filter(class_group_id=class_group)

        return queryset