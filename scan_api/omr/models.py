from django.db import models
from django.utils.translation import gettext_lazy as _

from core.models import BaseModel


class Exam(BaseModel):
    class Meta(BaseModel.Meta):
        verbose_name = _("Prova")
        verbose_name_plural = _("Provas")
        ordering = ["-created_at"]

    title = models.CharField(
        _("Título"),
        max_length=150,
    )

    description = models.TextField(
        _("Descrição"),
        blank=True,
        null=True,
    )

    answer_key = models.JSONField(
        _("Gabarito"),
        help_text=_("Lista de respostas corretas. Exemplo: ['A', 'B', 'C']."),
    )

    is_active = models.BooleanField(
        _("Ativa"),
        default=True,
    )

    def __str__(self):
        return self.title


class ScanResult(BaseModel):
    class Meta(BaseModel.Meta):
        verbose_name = _("Resultado da leitura")
        verbose_name_plural = _("Resultados das leituras")
        ordering = ["-created_at"]

    exam = models.ForeignKey(
        Exam,
        on_delete=models.CASCADE,
        related_name="scan_results",
        verbose_name=_("Prova"),
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