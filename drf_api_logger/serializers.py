from rest_framework import serializers

from drf_api_logger.models import APILogsModel


class APILoggerListSerializer(serializers.ModelSerializer):
    class Meta:
        model = APILogsModel
        fields = [
            "request_id",
            "api",
            "method",
            "browser",
            "client_ip_address",
            "execution_time",
            "result_code",
            "user",
            "added_on",
        ]


class APILoggerDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = APILogsModel
        fields = [
            "request_id",
            "api",
            "method",
            "headers",
            "content_type",
            "browser",
            "location",
            "body",
            "execution_time",
            "status_code",
            "result_code",
            "response",
            "user",
            "retry_times",
            "added_on",
        ]
