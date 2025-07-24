from django.db import models
from django.conf import settings

from drf_api_logger.utils import database_log_enabled


if database_log_enabled():
    """
    Load models only if DRF_API_LOGGER_DATABASE is True
    """
    class BaseModel(models.Model):
        id = models.BigAutoField(primary_key=True)

        added_on = models.DateTimeField()

        def __str__(self):
            return str(self.id)

        class Meta:
            abstract = True
            ordering = ('-added_on',)


    class APILogsModel(BaseModel):
        api = models.CharField(max_length=1024, help_text='API URL')
        headers = models.TextField()
        body = models.TextField()
        method = models.CharField(max_length=10, db_index=True)
        client_ip_address = models.CharField(max_length=50)
        response = models.TextField()
        status_code = models.PositiveSmallIntegerField(help_text='Response status code', db_index=True)
        execution_time = models.DecimalField(decimal_places=5, max_digits=8,
                                             help_text='Server execution time (Not complete response time.)')
        tracing_id = models.UUIDField(null=True, blank=True, help_text='Tracing request', db_index=True)
        request_user = models.ForeignKey(to=settings.AUTH_USER_MODEL, null=True, blank=True, db_constraint=False, on_delete=models.DO_NOTHING)
        result_code = models.PositiveSmallIntegerField(help_text='API result code', null=True, blank=True, db_index=True)
        retry_times = models.IntegerField(default=0)

        def __str__(self):
            return self.api

        class Meta:
            db_table = 'drf_api_logs'
            verbose_name = 'API Log'
            verbose_name_plural = 'API Logs'

    class APILogsModel2(APILogsModel):
        class Meta:
            proxy = True
            managed = False
            verbose_name = "API Log2"
            verbose_name_plural = "API Logs2"
