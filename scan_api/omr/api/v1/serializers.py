from rest_framework import serializers

from omr.models import Exam, ScanResult

from drf_spectacular.utils import extend_schema_field


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

    def validate_questions_count(self, value):
        if value < 8 or value > 30:
            raise serializers.ValidationError(
                "A quantidade de questões deve estar entre 8 e 30."
            )

        return value

    def validate_options_count(self, value):
        if value not in [4, 5]:
            raise serializers.ValidationError(
                "A quantidade de alternativas deve ser 4 ou 5."
            )

        return value

    def validate(self, attrs):
        questions_count = attrs.get("questions_count")
        options_count = attrs.get("options_count")
        answer_key = attrs.get("answer_key")

        if self.instance:
            questions_count = questions_count or self.instance.questions_count
            options_count = options_count or self.instance.options_count
            answer_key = answer_key if answer_key is not None else self.instance.answer_key

        if not answer_key:
            raise serializers.ValidationError({
                "answer_key": "O gabarito da prova é obrigatório."
            })

        if not isinstance(answer_key, list):
            raise serializers.ValidationError({
                "answer_key": "O gabarito deve ser uma lista de respostas."
            })

        if len(answer_key) != questions_count:
            raise serializers.ValidationError({
                "answer_key": (
                    f"O gabarito deve ter exatamente {questions_count} respostas."
                )
            })

        valid_options = [chr(65 + i) for i in range(options_count)]

        invalid_answers = [
            answer for answer in answer_key
            if answer not in valid_options
        ]

        if invalid_answers:
            raise serializers.ValidationError({
                "answer_key": (
                    f"As respostas devem estar entre {valid_options}. "
                    f"Valores inválidos: {invalid_answers}"
                )
            })

        return attrs


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

    student_identified = serializers.SerializerMethodField()
    warnings = serializers.SerializerMethodField()

    class Meta:
        model = ScanResult
        fields = [
            "id",
            "exam",
            "exam_title",
            "student",
            "student_name",
            "student_identified",
            "student_number",
            "answers",
            "score",
            "total_questions",
            "image",
            "warnings",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "exam_title",
            "student",
            "student_name",
            "student_identified",
            "student_number",
            "answers",
            "score",
            "total_questions",
            "warnings",
            "created_at",
            "updated_at",
        ]

    @extend_schema_field(bool)
    def get_student_identified(self, obj):
        return obj.student is not None

    @extend_schema_field(list[str])
    def get_warnings(self, obj):
        warnings = []

        if not obj.student_number or "?" in obj.student_number:
            warnings.append(
                "Não foi possível identificar corretamente o número do aluno."
            )

        if obj.student_number and "?" not in obj.student_number and obj.student is None:
            warnings.append(
                "O número do aluno foi lido, mas nenhum aluno correspondente foi encontrado na turma da prova."
            )

        if obj.answers:
            blank_or_invalid = [
                index + 1
                for index, answer in enumerate(obj.answers)
                if answer is None
            ]

            if blank_or_invalid:
                warnings.append(
                    f"Existem questões em branco ou com dupla marcação: {blank_or_invalid}."
                )

        return warnings
    

class ScanUploadSerializer(serializers.Serializer):
    exam_id = serializers.IntegerField()
    image = serializers.ImageField()