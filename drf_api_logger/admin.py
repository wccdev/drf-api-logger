from django.conf import settings
from django.contrib import admin, messages
from django.db.models import Count, F, TextField
from django.forms import Textarea
from django.http import HttpResponse
from django.urls import reverse
from django.utils.html import escape, format_html
from django.templatetags.static import static
from rest_framework.test import APIClient

from drf_api_logger.utils import database_log_enabled
from .constants import VIEW_REVERSE_BASENAME

if database_log_enabled():
    from drf_api_logger.models import APILogsModel
    from drf_api_logger.models import APILogsModel2
    from django.utils.translation import gettext_lazy as _
    import csv


    class ExportCsvMixin:
        def export_as_csv(self, request, queryset):
            meta = self.model._meta
            field_names = [field.name for field in meta.fields]

            response = HttpResponse(content_type='text/csv')
            response['Content-Disposition'] = 'attachment; filename={}.csv'.format(meta)
            writer = csv.writer(response)

            writer.writerow(field_names)
            for obj in queryset:
                writer.writerow([getattr(obj, field) for field in field_names])

            return response

        export_as_csv.short_description = "Export Selected"

    class SlowAPIsFilter(admin.SimpleListFilter):
        title = _('API Performance')

        # Parameter for the filter that will be used in the URL query.
        parameter_name = 'api_performance'

        def __init__(self, request, params, model, model_admin):
            super().__init__(request, params, model, model_admin)
            if hasattr(settings, 'DRF_API_LOGGER_SLOW_API_ABOVE'):
                if isinstance(settings.DRF_API_LOGGER_SLOW_API_ABOVE, int):  # Making sure for integer value.
                    self._DRF_API_LOGGER_SLOW_API_ABOVE = settings.DRF_API_LOGGER_SLOW_API_ABOVE / 1000  # Converting to seconds.

        def lookups(self, request, model_admin):
            """
            Returns a list of tuples. The first element in each
            tuple is the coded value for the option that will
            appear in the URL query. The second element is the
            human-readable name for the option that will appear
            in the right sidebar.
            """
            slow = 'Slow'
            fast = 'Fast'
            if hasattr(settings, 'DRF_API_LOGGER_SLOW_API_ABOVE'):
                slow += ', >={}ms'.format(settings.DRF_API_LOGGER_SLOW_API_ABOVE)
                fast += ', <{}ms'.format(settings.DRF_API_LOGGER_SLOW_API_ABOVE)

            return (
                ('slow', _(slow)),
                ('fast', _(fast)),
            )

        def queryset(self, request, queryset):
            """
            Returns the filtered queryset based on the value
            provided in the query string and retrievable via
            `self.value()`.
            """
            # to decide how to filter the queryset.
            if self.value() == 'slow':
                return queryset.filter(execution_time__gte=self._DRF_API_LOGGER_SLOW_API_ABOVE)
            if self.value() == 'fast':
                return queryset.filter(execution_time__lt=self._DRF_API_LOGGER_SLOW_API_ABOVE)

            return queryset

    class APILogsAdmin(admin.ModelAdmin, ExportCsvMixin):

        actions = ["export_as_csv", "retry"]

        def __init__(self, model, admin_site):
            super().__init__(model, admin_site)
            self._DRF_API_LOGGER_TIMEDELTA = 0
            if hasattr(settings, 'DRF_API_LOGGER_SLOW_API_ABOVE'):
                if isinstance(settings.DRF_API_LOGGER_SLOW_API_ABOVE, int):  # Making sure for integer value.
                    self.list_filter += (SlowAPIsFilter,)
            if hasattr(settings, 'DRF_API_LOGGER_TIMEDELTA'):
                if isinstance(settings.DRF_API_LOGGER_TIMEDELTA, int):  # Making sure for integer value.
                    self._DRF_API_LOGGER_TIMEDELTA = settings.DRF_API_LOGGER_TIMEDELTA

        @admin.display(description="Execution time", ordering="execution_time")
        def get_execution_time(self, obj):
            if obj.execution_time < 1.0:
                return f"{int(obj.execution_time * 1000)}ms"

            return f"{obj.execution_time:.2f}s"

        @admin.display(description="Headers")
        def get_headers_with_copy(self, obj):
            content = escape(obj.headers)
            icon_url = static('drf_api_logger/img/copy-icon.svg')
            return format_html('''
                <div class="flex-container">
                    <div class="field-label">
                        <button type="button" class="copy-button" title="复制" aria-label="复制">
                            <img src="{}" alt="复制" class="copy-icon">
                            <span class="tooltip-text">复制</span>  <!-- 添加气泡框元素 -->
                        </button>
                    </div>
                    <div class="readonly"><pre>{}</pre></div>
                </div>
            ''', icon_url, content)

        @admin.display(description="Body")
        def get_body_with_copy(self, obj):
            content = escape(obj.body)
            icon_url = static('drf_api_logger/img/copy-icon.svg')
            return format_html('''
                <div class="flex-container">
                    <button type="button" class="copy-button" title="复制" aria-label="复制">
                        <img src="{}" alt="复制" class="copy-icon">
                        <span class="tooltip-text">复制</span>  <!-- 添加气泡框元素 -->
                    </button>
                    <div class="readonly"><pre>{}</pre></div>
                </div>
            ''', icon_url, content)

        @admin.display(description="Response")
        def get_response_with_copy(self, obj):
            content = escape(obj.response)
            icon_url = static('drf_api_logger/img/copy-icon.svg')
            return format_html('''
                <div class="flex-container">
                    <div class="field-label">
                        <button type="button" class="copy-button" title="复制" aria-label="复制">
                            <img src="{}" alt="复制" class="copy-icon">
                            <span class="tooltip-text">复制</span>  <!-- 添加气泡框元素 -->
                        </button>
                    </div>
                    <div class="readonly"><pre>{}</pre></div>
                </div>
            ''', icon_url, content)

        class Media:
            js = ('drf_api_logger/js/copy-buttons.js',)
            css = {
                'all': ('drf_api_logger/css/copy-buttons.css',)
            }

        list_per_page = 20
        ordering = ("-id",)
        list_display = ('id', 'api', 'method', 'result_code', 'get_execution_time', 'added_on',)
        list_filter = ('added_on', 'result_code', 'method',)
        search_fields = ('body', 'response', 'headers', 'api', 'tracing_id')
        readonly_fields = (
            'get_execution_time', 'client_ip_address', 'api',
            'get_headers_with_copy', 'get_body_with_copy', 'method', 'get_response_with_copy', 'status_code', 'added_on',
            'request_user', 'tracing_id', 'result_code',
        )
        fields = readonly_fields
        change_list_template = 'charts_change_list.html'
        change_form_template = 'change_form.html'
        date_hierarchy = 'added_on'
        formfield_overrides = {
            TextField: {
                'widget': Textarea(attrs={
                    'rows': 40,
                    'cols': 40,
                    # 其他自定义属性
                }),
            },
        }

        def changelist_view(self, request, extra_context=None):
            response = super(APILogsAdmin, self).changelist_view(request, extra_context)
            try:
                filtered_query_set = response.context_data["cl"].queryset
            except Exception:
                return response
            analytics_model = filtered_query_set.values('added_on__date').annotate(total=Count('id')).order_by('total')
            status_code_count_mode = filtered_query_set.values('id').values('result_code').annotate(
                total=Count('id')).order_by('result_code')
            status_code_count_keys = list()
            status_code_count_values = list()
            for item in status_code_count_mode:
                status_code_count_keys.append(item.get('result_code'))
                status_code_count_values.append(item.get('total'))
            extra_context = dict(
                analytics=analytics_model,
                status_code_count_keys=status_code_count_keys,
                status_code_count_values=status_code_count_values
            )
            response.context_data.update(extra_context)
            return response

        def get_queryset(self, request):
            drf_api_logger_default_database = 'default'
            if hasattr(settings, 'DRF_API_LOGGER_DEFAULT_DATABASE'):
                drf_api_logger_default_database = settings.DRF_API_LOGGER_DEFAULT_DATABASE
            return super(APILogsAdmin, self).get_queryset(request).using(drf_api_logger_default_database)

        def changeform_view(self, request, object_id=None, form_url='', extra_context=None):
            if request.GET.get('export', False):
                drf_api_logger_default_database = 'default'
                if hasattr(settings, 'DRF_API_LOGGER_DEFAULT_DATABASE'):
                    drf_api_logger_default_database = settings.DRF_API_LOGGER_DEFAULT_DATABASE
                export_queryset = self.get_queryset(request).filter(pk=object_id).using(drf_api_logger_default_database)
                return self.export_as_csv(request, export_queryset)
            return super(APILogsAdmin, self).changeform_view(request, object_id, form_url, extra_context)

        def has_add_permission(self, request, obj=None):
            return False

        def has_change_permission(self, request, obj=None):
            return False

        def retry(self, request, queryset):
            """
            Perform retry
            """

            if len(queryset) > 1:
                self.message_user(
                    request, "You cannot retry in batch!", level=messages.ERROR
                )
                return

            api_log = queryset.first()
            client = APIClient(HTTP_USER_AGENT="Django/RetryClient")

            if api_log.request_user:
                client.force_authenticate(user=api_log.request_user)

            getattr(client, api_log.method.lower())(
                api_log.api,
                data=api_log.body,
                format="json",
                HTTP_Tracing_ID=str(api_log.tracing_id),
            )
            api_log.retry_times = F("retry_times") + 1
            api_log.save(update_fields=["retry_times"])
            self.message_user(request, "重试成功!", level=messages.INFO)



    admin.site.register(APILogsModel, APILogsAdmin)


    class APILogsRebornAdmin(admin.ModelAdmin):
        change_list_template = "reborn_list.html"

        def get_queryset(self, request):
            return super().get_queryset(request).none()

        def has_add_permission(self, request, obj=None):
            return False

        def has_change_permission(self, request, obj=None):
            return False

        def changelist_view(self, request, extra_context=None):
            from drf_api_logger.apps import LoggerConfig

            extra_context = extra_context or {}
            try:
                base_fetch_api = reverse(f"{LoggerConfig.name}:{VIEW_REVERSE_BASENAME}-list")
            except:
                err_msg = """
                请先在项目urlpatterns中添加drf_api_logger接口, 例如\n
                urlpatterns = [\n
                    ...\n
                    path("api/drf-api-logs/", include("drf_api_logger.urls")),\n
                    ...\n
                ]
                """
                self.message_user(request, err_msg, level=messages.ERROR)
                base_fetch_api = ""
            extra_context["base_fetch_api"] = base_fetch_api
            return super().changelist_view(request, extra_context=extra_context)

    admin.site.register(APILogsModel2, APILogsRebornAdmin)
