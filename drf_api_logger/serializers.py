from rest_framework import serializers

from drf_api_logger.models import APILogsModel


class APILoggerListSerializer(serializers.ModelSerializer):
    request_user = serializers.CharField(source="user", label="request user")

    class Meta:
        model = APILogsModel
        exclude = ["status_code"]

