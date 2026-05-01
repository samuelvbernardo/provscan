import os
import tempfile

from django.contrib import admin
from django.utils.translation import gettext_lazy as _

from omr.models import Exam, ScanResult
from omr.services.pipeline import process_image


@admin.register(Exam)
class ExamAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "title",
        "is_active",
        "created_at",
        "updated_at",
    )

    search_fields = (
        "title",
        "description",
    )

    list_filter = (
        "is_active",
        "created_at",
    )

    readonly_fields = (
        "created_at",
        "updated_at",
        "is_deleted",
        "deleted_at",
    )

    fieldsets = (
        (_("Informações da prova"), {
            "fields": (
                "title",
                "description",
                "answer_key",
                "is_active",
            )
        }),
        (_("Controle"), {
            "fields": (
                "created_at",
                "updated_at",
                "is_deleted",
                "deleted_at",
            )
        }),
    )


@admin.register(ScanResult)
class ScanResultAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "exam",
        "student_number",
        "score",
        "total_questions",
        "created_at",
    )

    search_fields = (
        "student_number",
        "exam__title",
    )

    list_filter = (
        "exam",
        "created_at",
    )

    readonly_fields = (
        "student_number",
        "answers",
        "score",
        "total_questions",
        "created_at",
        "updated_at",
        "is_deleted",
        "deleted_at",
    )

    fieldsets = (
        (_("Envio para leitura"), {
            "fields": (
                "exam",
                "image",
            )
        }),
        (_("Resultado da leitura"), {
            "fields": (
                "student_number",
                "answers",
                "score",
                "total_questions",
            )
        }),
        (_("Controle"), {
            "fields": (
                "created_at",
                "updated_at",
                "is_deleted",
                "deleted_at",
            )
        }),
    )

    def save_model(self, request, obj, form, change):
        image_file = form.cleaned_data.get("image")

        should_process = image_file and (not change or "image" in form.changed_data or "exam" in form.changed_data)

        if should_process:
            suffix = os.path.splitext(image_file.name)[1] or ".jpg"

            with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as temp_file:
                for chunk in image_file.chunks():
                    temp_file.write(chunk)

                temp_path = temp_file.name

            try:
                result = process_image(
                    path=temp_path,
                    gabarito=obj.exam.answer_key,
                )
            finally:
                if os.path.exists(temp_path):
                    os.remove(temp_path)

            obj.student_number = result["numero_aluno"]
            obj.answers = result["respostas"]
            obj.score = result["nota"]
            obj.total_questions = len(obj.exam.answer_key)

        super().save_model(request, obj, form, change)