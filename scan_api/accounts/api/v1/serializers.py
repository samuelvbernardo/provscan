from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers

from accounts.validators import validate_email_domain_exists


User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            "id",
            "email",
            "first_name",
            "last_name",
            "is_active",
            "is_staff",
            "date_joined",
        ]
        read_only_fields = fields


class UserCreateSerializer(serializers.ModelSerializer):
    password = serializers.CharField(
        write_only=True,
        required=True,
        trim_whitespace=False,
    )

    password_confirm = serializers.CharField(
        write_only=True,
        required=True,
        trim_whitespace=False,
    )

    class Meta:
        model = User
        fields = [
            "id",
            "email",
            "password",
            "password_confirm",
        ]
        read_only_fields = ["id"]

    def validate_email(self, value):
        value = value.lower().strip()

        validate_email_domain_exists(value)

        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError(
                "Já existe um usuário cadastrado com este email."
            )

        return value

    def validate(self, attrs):
        password = attrs.get("password")
        password_confirm = attrs.pop("password_confirm", None)

        if password != password_confirm:
            raise serializers.ValidationError({
                "password_confirm": "As senhas não conferem."
            })

        validate_password(password)

        return attrs

    def create(self, validated_data):
        password = validated_data.pop("password")

        user = User.objects.create_user(
            password=password,
            **validated_data,
        )

        return user