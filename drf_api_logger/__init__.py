import os
from drf_api_logger.events import Events

try:
    from asgiref.local import Local
except ImportError:
    from threading import local as Local  # noqa


local = Local()


REQUEST_ID_HEADER_SETTING = "DRF_API_LOGGER_REQUEST_ID_HEADER"
REQUEST_ID_RESPONSE_HEADER_SETTING = "DRF_API_LOGGER_REQUEST_ID_RESPONSE_HEADER"


if os.environ.get("RUN_MAIN", None) != "true":
    default_app_config = "drf_api_logger.apps.LoggerConfig"

API_LOGGER_SIGNAL = Events()
