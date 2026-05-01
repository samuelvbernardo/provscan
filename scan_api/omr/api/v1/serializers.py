from rest_framework import serializers

from omr.models import Exam, ScanResult


class ExamSerializer(serializers.ModelSerializer):
    class Meta:
        model = Exam
        fields = [
            "id",
            "title",
            "description",
            "answer_key",
            "is_active",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "created_at",
            "updated_at",
        ]


class ScanResultSerializer(serializers.ModelSerializer):
    exam_title = serializers.CharField(
        source="exam.title",
        read_only=True
    )

    class Meta:
        model = ScanResult
        fields = [
            "id",
            "exam",
            "exam_title",
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
