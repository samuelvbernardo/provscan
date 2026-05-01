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

    def delete(self, using=None, keep_parents=False):
        self.is_deleted = True
        self.deleted_at = timezone.now()
        self.save(update_fields=["is_deleted", "deleted_at", "updated_at"])

    def restore(self):
        self.is_deleted = False
        self.deleted_at = None
        self.save(update_fields=["is_deleted", "deleted_at", "updated_at"])