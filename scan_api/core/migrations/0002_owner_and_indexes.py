import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("core", "0001_initial"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        # 1. Adiciona owner em ClassGroup (nullable para dados existentes)
        migrations.AddField(
            model_name="classgroup",
            name="owner",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="class_groups",
                to=settings.AUTH_USER_MODEL,
                verbose_name="Proprietário",
            ),
        ),
        # 2. Remove unique constraint de name (agora é única por owner)
        migrations.AlterField(
            model_name="classgroup",
            name="name",
            field=models.CharField(
                help_text="Exemplo: 5º Ano A, 9º Ano B, 1ª Série C.",
                max_length=100,
                verbose_name="Nome da turma",
            ),
        ),
        # 3. Índices em ClassGroup
        migrations.AddIndex(
            model_name="classgroup",
            index=models.Index(
                fields=["owner", "is_deleted"],
                name="core_classgroup_owner_deleted_idx",
            ),
        ),
        migrations.AddIndex(
            model_name="classgroup",
            index=models.Index(
                fields=["is_deleted"],
                name="core_classgroup_is_deleted_idx",
            ),
        ),
        migrations.AddIndex(
            model_name="classgroup",
            index=models.Index(
                fields=["is_active"],
                name="core_classgroup_is_active_idx",
            ),
        ),
        # 4. Índices em Student
        migrations.AddIndex(
            model_name="student",
            index=models.Index(
                fields=["class_group", "number", "is_deleted"],
                name="core_student_cg_num_deleted_idx",
            ),
        ),
        migrations.AddIndex(
            model_name="student",
            index=models.Index(
                fields=["is_deleted"],
                name="core_student_is_deleted_idx",
            ),
        ),
        migrations.AddIndex(
            model_name="student",
            index=models.Index(
                fields=["is_active"],
                name="core_student_is_active_idx",
            ),
        ),
    ]
