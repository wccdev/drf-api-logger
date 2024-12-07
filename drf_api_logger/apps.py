from django.apps import AppConfig


class LoggerConfig(AppConfig):
    name = 'drf_api_logger'
    verbose_name = 'DRF API Logger'

    def ready(self):
        from drf_api_logger.start_logger_when_server_starts import start_logger_thread
        start_logger_thread()
