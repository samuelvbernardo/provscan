import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("omr", "0005_alter_exam_options_count"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        # 1. Adiciona owner em Exam (nullable para dados existentes)
        migrations.AddField(
            model_name="exam",
            name="owner",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="exams",
                to=settings.AUTH_USER_MODEL,
                verbose_name="Proprietário",
            ),
        ),
        # 2. Índices em Exam
        migrations.AddIndex(
            model_name="exam",
            index=models.Index(
                fields=["owner", "is_deleted"],
                name="omr_exam_owner_deleted_idx",
            ),
        ),
        migrations.AddIndex(
            model_name="exam",
            index=models.Index(
                fields=["is_deleted"],
                name="omr_exam_is_deleted_idx",
            ),
        ),
        migrations.AddIndex(
            model_name="exam",
            index=models.Index(
                fields=["is_active"],
                name="omr_exam_is_active_idx",
            ),
        ),
        # 3. Índices em ScanResult
        migrations.AddIndex(
            model_name="scanresult",
            index=models.Index(
                fields=["exam", "is_deleted"],
                name="omr_scanresult_exam_deleted_idx",
            ),
        ),
        migrations.AddIndex(
            model_name="scanresult",
            index=models.Index(
                fields=["student"],
                name="omr_scanresult_student_idx",
            ),
        ),
        migrations.AddIndex(
            model_name="scanresult",
            index=models.Index(
                fields=["is_deleted"],
                name="omr_scanresult_is_deleted_idx",
            ),
        ),
    ]
