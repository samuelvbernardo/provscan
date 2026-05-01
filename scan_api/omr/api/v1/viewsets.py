import os
import tempfile

from django.core.files.base import ContentFile
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from omr.api.v1.serializers import (
    ExamSerializer,
    ScanResultSerializer,
    ScanUploadSerializer,
)
from omr.models import Exam, ScanResult
from omr.services.pipeline import process_image
from drf_spectacular.utils import extend_schema


class ExamViewSet(viewsets.ModelViewSet):
    queryset = Exam.active.all()
    serializer_class = ExamSerializer


class ScanResultViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = ScanResult.active.select_related("exam").all()
    serializer_class = ScanResultSerializer


class OMRViewSet(viewsets.ViewSet):
    serializer_class = ScanUploadSerializer

    @extend_schema(
        request=ScanUploadSerializer,
        responses={201: ScanResultSerializer},
    )
    @action(detail=False, methods=["post"], url_path="scan")
    def scan(self, request):
        serializer = ScanUploadSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        exam_id = serializer.validated_data["exam_id"]
        image = serializer.validated_data["image"]

        try:
            exam = Exam.active.get(id=exam_id, is_active=True)
        except Exam.DoesNotExist:
            return Response(
                {"detail": "Prova não encontrada ou inativa."},
                status=status.HTTP_404_NOT_FOUND,
            )

        suffix = os.path.splitext(image.name)[1] or ".jpg"

        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as temp_file:
            for chunk in image.chunks():
                temp_file.write(chunk)

            temp_path = temp_file.name

        try:
            result = process_image(
                path=temp_path,
                gabarito=exam.answer_key,
            )
        finally:
            if os.path.exists(temp_path):
                os.remove(temp_path)

        scan_result = ScanResult.objects.create(
            exam=exam,
            student_number=result["numero_aluno"],
            answers=result["respostas"],
            score=result["nota"],
            total_questions=len(exam.answer_key),
        )

        image.seek(0)
        scan_result.image.save(
            image.name,
            ContentFile(image.read()),
            save=True,
        )

        output_serializer = ScanResultSerializer(scan_result)

        return Response(
            output_serializer.data,
            status=status.HTTP_201_CREATED,
        )