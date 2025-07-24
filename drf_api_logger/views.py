import json
from json.decoder import JSONDecodeError

import django_filters
from django_filters.rest_framework.backends import DjangoFilterBackend
from rest_framework import mixins
from rest_framework import serializers
from rest_framework.filters import OrderingFilter
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from drf_api_logger.models import APILogsModel


class ApiLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = APILogsModel
        exclude = (
            "headers",
            "body",
            "response",
        )


class ApiLogDetailSerializer(ApiLogSerializer):
    class Meta:
        model = APILogsModel
        fields = "__all__"

    def to_representation(self, instance):
        ret = super().to_representation(instance)
        for i in ["headers", "body", "response"]:
            try:
                ret[f"{i}_json"] = json.loads(ret[i])
            except (JSONDecodeError, TypeError, ValueError):
                ret[f"{i}_json"] = None
        return ret


class InnerPagination(PageNumberPagination):
    page_size_query_param = "page_size"


class ApiLogFilterSet(django_filters.FilterSet):
    added_on = django_filters.DateTimeFromToRangeFilter()
    api = django_filters.CharFilter(lookup_expr="icontains")
    tracing_id = django_filters.CharFilter(lookup_expr="icontains")

    class Meta:
        model = APILogsModel
        fields = (
            "added_on",
            "api",
            "tracing_id",
        )


class ApiLogForAdminViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    GenericViewSet,
):
    queryset = APILogsModel.objects.all()
    serializer_class = ApiLogSerializer
    pagination_class = InnerPagination
    filter_backends = (DjangoFilterBackend, OrderingFilter)
    filterset_class = ApiLogFilterSet
    ordering = ("-id",)

    def get_queryset(self):
        if not self.request.user.is_superuser:
            return self.queryset.none()
        return super().get_queryset()

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = ApiLogDetailSerializer(instance)
        return Response(serializer.data)

    # @action(detail=False)
    # def select_info(self, request, *args, **kwargs):
    #     values = {
    #         "status_codes": self.queryset.exclude(status_code__isnull=True).values_list("status_code", flat=True).distinct(),
    #         "methods": self.queryset.values_list("method", flat=True).distinct()
    #     }
    #     return Response(values)
