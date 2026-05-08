import os
import tempfile

from django.core.files.base import ContentFile
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.throttling import UserRateThrottle
from drf_spectacular.utils import extend_schema

from core.models import Student
from omr.api.v1.serializers import (
    ExamSerializer,
    ScanResultSerializer,
    ScanUploadSerializer,
)
from omr.models import Exam, ScanResult
from omr.services.pipeline import process_image
from omr.services.template_generator import generate_exam_template


class ExamViewSet(viewsets.ModelViewSet):
    queryset = Exam.active.all()
    serializer_class = ExamSerializer

    def perform_create(self, serializer):
        exam = serializer.save()

        relative_path = generate_exam_template(exam)
        exam.template_file = relative_path
        exam.save(update_fields=["template_file"])

    def perform_update(self, serializer):
        exam = serializer.save()

        relative_path = generate_exam_template(exam)
        exam.template_file = relative_path
        exam.save(update_fields=["template_file"])


class ScanResultViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = ScanResult.active.select_related(
        "exam",
        "student",
    ).all()
    serializer_class = ScanResultSerializer


class ScanRateThrottle(UserRateThrottle):
    scope = 'scan'


class OMRViewSet(viewsets.ViewSet):
    serializer_class = ScanUploadSerializer
    throttle_classes = [ScanRateThrottle]

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
                questions_count=exam.questions_count,
                options_count=exam.options_count,
            )
        except Exception:
            return Response(
                {"detail": "Não foi possível processar a imagem. Verifique se o cartão está bem iluminado, centralizado e sem dobras."},
                status=status.HTTP_422_UNPROCESSABLE_ENTITY,
            )
        finally:
            if os.path.exists(temp_path):
                os.remove(temp_path)

        student = None

        try:
            student_number_int = int(result["numero_aluno"])
        except (TypeError, ValueError):
            student_number_int = None

        if exam.class_group and student_number_int is not None:
            student = Student.active.filter(
                class_group=exam.class_group,
                number=student_number_int,
                is_active=True,
            ).first()

        scan_result = ScanResult.objects.create(
            exam=exam,
            student=student,
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