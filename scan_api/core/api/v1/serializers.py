from drf_spectacular.utils import extend_schema_field
from rest_framework import serializers

from core.models import ClassGroup, Student


class ClassGroupSerializer(serializers.ModelSerializer):
    students_count = serializers.SerializerMethodField()

    class Meta:
        model = ClassGroup
        fields = [
            "id",
            "name",
            "school_year",
            "is_active",
            "students_count",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "students_count",
            "created_at",
            "updated_at",
        ]

    @extend_schema_field(int)
    def get_students_count(self, obj):
        # Usa o valor anotado pelo queryset quando disponível (sem N+1).
        # Faz a contagem direta apenas em create/update (objeto único, aceitável).
        if hasattr(obj, "students_count"):
            return obj.students_count
        return obj.students.filter(is_deleted=False).count()


class StudentSerializer(serializers.ModelSerializer):
    class_group_name = serializers.CharField(
        source="class_group.name",
        read_only=True,
    )

    class Meta:
        model = Student
        fields = [
            "id",
            "class_group",
            "class_group_name",
            "number",
            "name",
            "is_active",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "class_group_name",
            "created_at",
            "updated_at",
        ]

    def validate_number(self, value):
        if value < 0 or value > 99:
            raise serializers.ValidationError("O número do aluno deve estar entre 0 e 99.")

        return value

    def validate(self, attrs):
        class_group = attrs.get("class_group")
        number = attrs.get("number")

        if self.instance:
            class_group = class_group or self.instance.class_group
            number = number if number is not None else self.instance.number

        exists = Student.active.filter(
            class_group=class_group,
            number=number,
            is_active=True,
        )

        if self.instance:
            exists = exists.exclude(id=self.instance.id)

        if exists.exists():
            raise serializers.ValidationError(
                {"number": "Já existe um aluno com esse número nessa turma."}
            )

        return attrs
