from rest_framework import serializers

from omr.models import Exam, ScanResult


class ExamSerializer(serializers.ModelSerializer):
    class_group_name = serializers.CharField(
        source="class_group.name",
        read_only=True
    )

    class Meta:
        model = Exam
        fields = [
            "id",
            "title",
            "description",
            "class_group",
            "class_group_name",
            "questions_count",
            "options_count",
            "answer_key",
            "template_file",
            "is_active",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "class_group_name",
            "template_file",
            "created_at",
            "updated_at",
        ]


class ScanResultSerializer(serializers.ModelSerializer):
    exam_title = serializers.CharField(
        source="exam.title",
        read_only=True
    )
    student_name = serializers.CharField(
        source="student.name",
        read_only=True,
        allow_null=True
    )

    class Meta:
        model = ScanResult
        fields = [
            "id",
            "exam",
            "exam_title",
            "student",
            "student_name",
            "student_number",
            "answers",
            "score",
            "total_questions",
            "image",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "exam_title",
            "student",
            "student_name",
            "student_number",
            "answers",
            "score",
            "total_questions",
            "created_at",
            "updated_at",
        ]


class ScanUploadSerializer(serializers.Serializer):
    exam_id = serializers.IntegerField()
    image = serializers.ImageField()