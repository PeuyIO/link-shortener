from urllib.parse import urlparse

from django.conf import settings
from rest_framework import serializers

from .models import Link


class LinkSerializer(serializers.ModelSerializer):
    short_url = serializers.SerializerMethodField()
    clicks_count = serializers.SerializerMethodField()

    class Meta:
        model = Link
        fields = (
            "id",
            "original_url",
            "short_code",
            "short_url",
            "clicks_count",
            "created_at",
        )
        read_only_fields = (
            "id",
            "short_code",
            "short_url",
            "clicks_count",
            "created_at",
        )

    def validate_original_url(self, value):
        parsed_url = urlparse(value)

        if parsed_url.scheme not in ("http", "https"):
            raise serializers.ValidationError(
                "Разрешены только URL с протоколами http и https."
            )

        if not parsed_url.netloc:
            raise serializers.ValidationError(
                "Укажите корректный URL с доменным именем."
            )

        return value

    def get_short_url(self, obj):
        base_url = settings.SHORT_URL_BASE.rstrip("/")
        return f"{base_url}/{obj.short_code}"

    def get_clicks_count(self, obj):
        return obj.clicks.count()

    def create(self, validated_data):
        request = self.context.get("request")

        if request is None or not request.user.is_authenticated:
            raise serializers.ValidationError(
                "Для создания ссылки необходимо авторизоваться."
            )

        return Link.objects.create(
            owner=request.user,
            **validated_data,
        )