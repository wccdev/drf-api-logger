from rest_framework.viewsets import ReadOnlyModelViewSet

from drf_api_logger.models import APILogsModel
from drf_api_logger.serializers import APILoggerListSerializer


class APILoggerViewSet(ReadOnlyModelViewSet):
    """
    A simple ViewSet for viewing api logs
    """
    queryset = APILogsModel.objects.select_related('request_user')
    serializer_class = APILoggerListSerializer
