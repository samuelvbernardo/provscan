import os
import tempfile

from django.contrib import admin
from django.utils.translation import gettext_lazy as _

from core.models import Student
from omr.models import Exam, ScanResult
from omr.services.pipeline import process_image
from omr.services.template_generator import generate_exam_template


@admin.register(Exam)
class ExamAdmin(admin.ModelAdmin):
    filter_horizontal = ("class_groups",)

    def get_class_groups(self, obj):
        return ", ".join(obj.class_groups.values_list("name", flat=True).order_by("name")) or "—"

    get_class_groups.short_description = "Turmas"

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)

        should_generate = (
            not obj.template_file
            or "questions_count" in form.changed_data
            or "options_count" in form.changed_data
            or "title" in form.changed_data
            or "class_groups" in form.changed_data
        )

        if should_generate:
            relative_path = generate_exam_template(obj)
            obj.template_file = relative_path
            obj.save(update_fields=["template_file"])

    list_display = (
        "id",
        "title",
        "get_class_groups",
        "questions_count",
        "options_count",
        "is_active",
        "created_at",
    )

    search_fields = (
        "title",
        "description",
        "class_groups__name",
    )

    list_filter = (
        "class_groups",
        "is_active",
        "created_at",
    )

    readonly_fields = (
        "created_at",
        "updated_at",
        "is_deleted",
        "deleted_at",
        "template_file",
    )

    fieldsets = (
        (
            _("Informações da prova"),
            {
                "fields": (
                    "title",
                    "description",
                    "class_groups",
                    "questions_count",
                    "options_count",
                    "answer_key",
                    "template_file",
                    "is_active",
                )
            },
        ),
        (
            _("Controle"),
            {
                "fields": (
                    "created_at",
                    "updated_at",
                    "is_deleted",
                    "deleted_at",
                )
            },
        ),
    )


@admin.register(ScanResult)
class ScanResultAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "exam",
        "student",
        "student_number",
        "score",
        "total_questions",
        "created_at",
    )

    search_fields = (
        "student_number",
        "student__name",
        "exam__title",
    )

    list_filter = (
        "exam",
        "student",
        "created_at",
    )

    readonly_fields = (
        "student",
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
        (
            _("Envio para leitura"),
            {
                "fields": (
                    "exam",
                    "image",
                )
            },
        ),
        (
            _("Resultado da leitura"),
            {
                "fields": (
                    "student",
                    "student_number",
                    "answers",
                    "score",
                    "total_questions",
                )
            },
        ),
        (
            _("Controle"),
            {
                "fields": (
                    "created_at",
                    "updated_at",
                    "is_deleted",
                    "deleted_at",
                )
            },
        ),
    )

    def save_model(self, request, obj, form, change):
        image_file = form.cleaned_data.get("image")

        should_process = image_file and (
            not change or "image" in form.changed_data or "exam" in form.changed_data
        )

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
                    questions_count=obj.exam.questions_count,
                    options_count=obj.exam.options_count,
                )
            finally:
                if os.path.exists(temp_path):
                    os.remove(temp_path)

            obj.student_number = result["numero_aluno"]
            obj.answers = result["respostas"]
            obj.score = result["nota"]
            obj.total_questions = len(obj.exam.answer_key)
            obj.student = None

            try:
                student_number_int = int(obj.student_number)
            except (TypeError, ValueError):
                student_number_int = None

            exam_class_groups = obj.exam.class_groups.all()
            if exam_class_groups.exists() and student_number_int is not None:
                obj.student = Student.active.filter(
                    class_group__in=exam_class_groups,
                    number=student_number_int,
                    is_active=True,
                ).first()

        super().save_model(request, obj, form, change)
