from django.conf import settings
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from core.managers import ActiveManager


class BaseModel(models.Model):
    created_at = models.DateTimeField(
        _("Criado em"),
        auto_now_add=True,
    )
    updated_at = models.DateTimeField(
        _("Atualizado em"),
        auto_now=True,
    )
    is_deleted = models.BooleanField(
        _("Excluído"),
        default=False,
    )
    deleted_at = models.DateTimeField(
        _("Excluído em"),
        null=True,
        blank=True,
    )

    objects = models.Manager()
    active = ActiveManager()

    class Meta:
        abstract = True
        indexes = [
            models.Index(fields=["is_deleted"]),
        ]

    def delete(self, using=None, keep_parents=False):
        self.is_deleted = True
        self.deleted_at = timezone.now()
        self.save(update_fields=["is_deleted", "deleted_at", "updated_at"])

    def restore(self):
        self.is_deleted = False
        self.deleted_at = None
        self.save(update_fields=["is_deleted", "deleted_at", "updated_at"])


class ClassGroup(BaseModel):
    class Meta(BaseModel.Meta):
        verbose_name = _("Turma")
        verbose_name_plural = _("Turmas")
        ordering = ["name"]
        indexes = [
            models.Index(fields=["owner", "is_deleted"]),
            models.Index(fields=["is_active"]),
        ]

    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="class_groups",
        verbose_name=_("Proprietário"),
        null=True,
        blank=True,
    )

    name = models.CharField(
        _("Nome da turma"),
        max_length=100,
        help_text=_("Exemplo: 5º Ano A, 9º Ano B, 1ª Série C."),
    )

    school_year = models.CharField(
        _("Ano/Série"),
        max_length=50,
        blank=True,
        null=True,
        help_text=_("Exemplo: 5º ano, 9º ano, 1ª série."),
    )

    is_active = models.BooleanField(
        _("Ativa"),
        default=True,
    )

    def __str__(self):
        return self.name


class Student(BaseModel):
    class Meta(BaseModel.Meta):
        verbose_name = _("Aluno")
        verbose_name_plural = _("Alunos")
        ordering = ["class_group", "number", "name"]
        indexes = [
            models.Index(fields=["class_group", "number", "is_deleted"]),
            models.Index(fields=["is_active"]),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=["class_group", "number"],
                condition=models.Q(is_deleted=False),
                name="unique_active_student_number_per_class",
            )
        ]

    class_group = models.ForeignKey(
        ClassGroup,
        on_delete=models.PROTECT,
        related_name="students",
        verbose_name=_("Turma"),
    )

    name = models.CharField(
        _("Nome do aluno"),
        max_length=150,
    )

    number = models.PositiveIntegerField(
        _("Número do aluno"),
        help_text=_("Número usado no gabarito. Exemplo: 1, 2, 25."),
    )

    is_active = models.BooleanField(
        _("Ativo"),
        default=True,
    )

    def __str__(self):
        return f"{self.number:02d} - {self.name}"
