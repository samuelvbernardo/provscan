import django.db.models.deletion
from django.db import migrations, models


def copy_class_groups(apps, schema_editor):
    Exam = apps.get_model("omr", "Exam")
    for exam in Exam.objects.exclude(class_group_id__isnull=True):
        exam.class_groups.add(exam.class_group_id)


class Migration(migrations.Migration):
    dependencies = [
        ("core", "0001_initial"),
        ("omr", "0003_alter_exam_answer_key_alter_exam_class_group_and_more"),
    ]

    operations = [
        # 1 — Add M2M with temp related_name to avoid clash with existing FK
        migrations.AddField(
            model_name="exam",
            name="class_groups",
            field=models.ManyToManyField(
                blank=True,
                related_name="exams_m2m",
                to="core.classgroup",
                verbose_name="Turmas",
            ),
        ),
        # 2 — Copy FK value into M2M
        migrations.RunPython(copy_class_groups, migrations.RunPython.noop),
        # 3 — Drop old FK
        migrations.RemoveField(model_name="exam", name="class_group"),
        # 4 — Rename related_name to final value
        migrations.AlterField(
            model_name="exam",
            name="class_groups",
            field=models.ManyToManyField(
                blank=True,
                related_name="exams",
                to="core.classgroup",
                verbose_name="Turmas",
            ),
        ),
    ]
