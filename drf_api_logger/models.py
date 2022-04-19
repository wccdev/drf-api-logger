import uuid

import requests
from django.conf import settings
from django.db import models
from django.utils.functional import cached_property
from user_agents import parse

from drf_api_logger.utils import database_log_enabled


if database_log_enabled():
    """
    Load models only if DRF_API_LOGGER_DATABASE is True
    """
    class BaseModel(models.Model):
        request_id = models.UUIDField(primary_key=True, default=uuid.uuid4)

        added_on = models.DateTimeField(db_index=True)

        def __str__(self):
            return self.request_id

        class Meta:
            abstract = True
            ordering = ('-added_on',)


    class APILogsModel(BaseModel):
        api = models.CharField(max_length=1024, help_text='API URL')
        headers = models.JSONField(null=True)
        body = models.JSONField(null=True)
        method = models.CharField(max_length=10, db_index=True)
        client_ip_address = models.CharField(max_length=50)
        response = models.JSONField(null=True)
        status_code = models.PositiveSmallIntegerField(help_text='Response status code', db_index=True)
        result_code = models.PositiveSmallIntegerField(help_text='Result code', null=True, db_index=True)
        request_user = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, on_delete=models.CASCADE, help_text="Request User")
        retry_times = models.IntegerField(default=0)
        execution_time = models.DecimalField(decimal_places=5, max_digits=8,
                                             help_text='Server execution time (Not complete response time.)')

        def __str__(self):
            return self.api

        @property
        def location2(self):
            api_url = "https://restapi.amap.com/v3/ip"
            if self.client_ip_address in ("localhost", "127.0.0.1", "0.0.0.0"):
                return self.client_ip_address

            amap_key = getattr(settings, "AMAP_WEB_API_KEY", None)
            if amap_key is None:
                return self.client_ip_address

            resp = requests.get(api_url, params={"key": amap_key, "ip": self.client_ip_address})
            data = resp.json()
            province, city = data["city"], data["province"]
            if city == "" or province == "":
                return self.client_ip_address

            if city == province:
                return f"{self.client_ip_address} {city}"

            return f"{self.client_ip_address} {province}{city}"

        @property
        def location(self):
            api_url = "https://sp1.baidu.com/8aQDcjqpAAV3otqbppnN2DJv/api.php"
            if self.client_ip_address in ("localhost", "127.0.0.1", "0.0.0.0"):
                return self.client_ip_address

            params = {
                "query": self.client_ip_address,
                "resource_id": 5809,
                "format": "json",
            }
            resp = requests.get(api_url, params=params)
            try:
                data = resp.json()
                location = data["data"][0]["location"]
                return f"{self.client_ip_address} {location}"
            except (KeyError, IndexError, TypeError):
                return self.client_ip_address

        @cached_property
        def user_agent(self):
            ua_string = self.headers.get("USER_AGENT")
            if ua_string is None:
                return None

            return parse(ua_string)

        @property
        def browser(self):
            ua = self.user_agent
            if ua is None:
                return "Unknown"

            return f"{ua.browser.family} {ua.browser.version_string}"

        class Meta:
            db_table = 'drf_api_logs'
            verbose_name = 'API Log'
            verbose_name_plural = 'API Logs'
