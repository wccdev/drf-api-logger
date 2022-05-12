from rest_framework import serializers

from drf_api_logger.models import APILogsModel


class APILoggerListSerializer(serializers.ModelSerializer):
    class Meta:
        model = APILogsModel
        fields = [
            "id",
            "request_id",
            "api",
            "method",
            "browser",
            "client_ip_address",
            "cost_time",
            "result_code",
            "user",
            "added_on",
        ]


class APILoggerDetailSerializer(serializers.ModelSerializer):
    user_agent = serializers.CharField()

    class Meta:
        model = APILogsModel
        fields = [
            "id",
            "request_id",
            "api",
            "method",
            "headers",
            "content_type",
            "user_agent",
            "location",
            "body",
            "cost_time",
            "status_code",
            "result_code",
            "user",
            "retry_times",
            "added_on",
            "response",
        ]
