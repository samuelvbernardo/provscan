import os
import tempfile

from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from django.http import HttpResponse
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
from omr.services.class_report import generate_class_report as generate_class_report_pdf
from omr.services.pipeline import process_image
from omr.services.report import generate_report_card
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

    @extend_schema(
        responses={(200, "application/pdf"): bytes},
        description="Retorna o cartão-resposta da prova em PDF.",
    )
    @action(detail=True, methods=["get"], url_path="template")
    def template(self, request, pk=None):
        exam = self.get_object()

        if not exam.template_file or not default_storage.exists(exam.template_file.name):
            relative_path = generate_exam_template(exam)
            exam.template_file = relative_path
            exam.save(update_fields=["template_file"])

        filename = f"cartao_resposta_{exam.id}.pdf"

        with exam.template_file.open("rb") as file:
            response = HttpResponse(file.read(), content_type="application/pdf")

        response["Content-Disposition"] = f'attachment; filename="{filename}"'
        return response

    @extend_schema(
        responses={(200, "application/pdf"): bytes},
        description="Gera relatório de resultados de múltiplas provas em PDF.",
    )
    @action(detail=False, methods=["get"], url_path="class-report")
    def class_report(self, request):
        raw = request.query_params.get("exam_ids", "")
        try:
            exam_ids = [int(x) for x in raw.split(",") if x.strip()]
        except ValueError:
            return Response(
                {"detail": "exam_ids inválidos."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if not exam_ids:
            return Response(
                {"detail": "Informe ao menos um exam_id."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        exams = list(
            Exam.active.filter(id__in=exam_ids)
            .prefetch_related("class_groups")
            .order_by("title")
        )

        if not exams:
            return Response(
                {"detail": "Nenhuma prova encontrada."},
                status=status.HTTP_404_NOT_FOUND,
            )

        try:
            pdf_bytes = generate_class_report_pdf(exams)
        except Exception:
            return Response(
                {"detail": "Não foi possível gerar o relatório."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        response = HttpResponse(pdf_bytes, content_type="application/pdf")
        response["Content-Disposition"] = 'attachment; filename="relatorio_turmas.pdf"'
        return response


class ScanResultViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = ScanResult.active.select_related(
        "exam",
        "student",
    ).prefetch_related("exam__class_groups").all()
    serializer_class = ScanResultSerializer

    @extend_schema(
        responses={(200, "application/pdf"): bytes},
        description="Gera e retorna o boletim individual do resultado em PDF.",
    )
    @action(detail=True, methods=["get"], url_path="report")
    def report(self, request, pk=None):
        scan_result = self.get_object()
        try:
            pdf_bytes = generate_report_card(scan_result)
        except Exception:
            return Response(
                {"detail": "Não foi possível gerar o boletim."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        student_label = (
            scan_result.student.name.replace(" ", "_")
            if scan_result.student
            else f"aluno_{scan_result.student_number}"
        )
        filename = f"boletim_{student_label}_{scan_result.id}.pdf"

        response = HttpResponse(pdf_bytes, content_type="application/pdf")
        response["Content-Disposition"] = f'attachment; filename="{filename}"'
        return response


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

        exam_class_groups = exam.class_groups.all()
        if exam_class_groups.exists() and student_number_int is not None:
            student = Student.active.filter(
                class_group__in=exam_class_groups,
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
