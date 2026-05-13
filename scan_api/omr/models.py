from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _

from core.models import BaseModel, ClassGroup, Student


class Exam(BaseModel):
    class Meta(BaseModel.Meta):
        verbose_name = _("Prova")
        verbose_name_plural = _("Provas")
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["owner", "is_deleted"]),
            models.Index(fields=["is_active"]),
        ]

    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="exams",
        verbose_name=_("Proprietário"),
        null=True,
        blank=True,
    )

    title = models.CharField(
        _("Título"),
        max_length=150,
    )

    description = models.TextField(
        _("Descrição"),
        blank=True,
        null=True,
    )

    class_groups = models.ManyToManyField(
        ClassGroup,
        blank=True,
        related_name="exams",
        verbose_name=_("Turmas"),
    )

    questions_count = models.PositiveIntegerField(
        _("Quantidade de questões"),
        default=8,
        help_text=_("Quantidade total de questões da prova. Mínimo 8 e máximo 30."),
    )

    options_count = models.PositiveIntegerField(
        _("Quantidade de alternativas"),
        default=4,
        help_text=_("Quantidade de alternativas por questão. Mínimo 4 e máximo 5."),
    )

    answer_key = models.JSONField(
        _("Gabarito"),
        help_text=_("Lista de respostas corretas. Exemplo: ['A', 'B', 'C', 'D']."),
    )

    template_file = models.FileField(
        _("Modelo de gabarito"),
        upload_to="exam_templates/",
        blank=True,
        null=True,
    )

    is_active = models.BooleanField(
        _("Ativa"),
        default=True,
    )

    def __str__(self):
        return self.title

    @property
    def options_labels(self):
        return [chr(65 + i) for i in range(self.options_count)]


class ScanResult(BaseModel):
    class Meta(BaseModel.Meta):
        verbose_name = _("Resultado da leitura")
        verbose_name_plural = _("Resultados das leituras")
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["exam", "is_deleted"]),
            models.Index(fields=["student"]),
        ]

    exam = models.ForeignKey(
        Exam,
        on_delete=models.CASCADE,
        related_name="scan_results",
        verbose_name=_("Prova"),
    )

    student = models.ForeignKey(
        Student,
        on_delete=models.PROTECT,
        related_name="scan_results",
        verbose_name=_("Aluno"),
        blank=True,
        null=True,
    )

    student_number = models.CharField(
        _("Número do aluno"),
        max_length=20,
    )

    answers = models.JSONField(
        _("Respostas"),
        help_text=_("Lista de respostas lidas pelo sistema."),
    )

    score = models.PositiveIntegerField(
        _("Nota"),
    )

    total_questions = models.PositiveIntegerField(
        _("Total de questões"),
    )

    image = models.ImageField(
        _("Imagem"),
        upload_to="scan_results/",
        blank=True,
        null=True,
    )

    def __str__(self):
        return f"{self.student_number} - {self.exam.title} - {self.score}/{self.total_questions}"
