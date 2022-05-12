from rest_framework.viewsets import ReadOnlyModelViewSet

from drf_api_logger.models import APILogsModel
from drf_api_logger.serializers import APILoggerListSerializer, APILoggerDetailSerializer


class APILoggerViewSet(ReadOnlyModelViewSet):
    """
    A simple ViewSet for viewing api logs
    """
    queryset = APILogsModel.objects.select_related('request_user')

    def get_serializer_class(self):
        if self.action == "list":
            return APILoggerListSerializer

        return APILoggerDetailSerializer
