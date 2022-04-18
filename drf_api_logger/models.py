from django.conf import settings
from django.db import models
from user_agents import parse

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
        headers = models.JSONField()
        body = models.JSONField()
        method = models.CharField(max_length=10, db_index=True)
        client_ip_address = models.CharField(max_length=50)
        response = models.JSONField()
        status_code = models.PositiveSmallIntegerField(help_text='Response status code', db_index=True)
        result_code = models.PositiveSmallIntegerField(help_text='Result code', null=True, db_index=True)
        request_user = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, on_delete=models.CASCADE, help_text="Request User")
        retry_times = models.IntegerField(default=0)
        execution_time = models.DecimalField(decimal_places=5, max_digits=8,
                                             help_text='Server execution time (Not complete response time.)')

        def __str__(self):
            return self.api

        @property
        def browser(self):
            ua_string = self.headers.get("USER_AGENT")
            if ua_string is None:
                return "Unknown"

            user_agent = parse(ua_string)
            return f"{user_agent.browser.family} {user_agent.browser.version_string}"

        class Meta:
            db_table = 'drf_api_logs'
            verbose_name = 'API Log'
            verbose_name_plural = 'API Logs'
