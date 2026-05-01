from django.contrib import admin
from django.utils.translation import gettext_lazy as _

from core.models import ClassGroup, Student


@admin.register(ClassGroup)
class ClassGroupAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "name",
        "school_year",
        "is_active",
        "created_at",
    )

    search_fields = (
        "name",
        "school_year",
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
        (_("Informações da turma"), {
            "fields": (
                "name",
                "school_year",
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


@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "number",
        "name",
        "class_group",
        "is_active",
    )

    search_fields = (
        "name",
        "class_group__name",
    )

    list_filter = (
        "class_group",
        "is_active",
    )

    readonly_fields = (
        "created_at",
        "updated_at",
        "is_deleted",
        "deleted_at",
    )

    fieldsets = (
        (_("Informações do aluno"), {
            "fields": (
                "class_group",
                "number",
                "name",
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