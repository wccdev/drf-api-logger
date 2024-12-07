# drf_api_logger/start_logger_when_server_starts.py

from drf_api_logger.utils import database_log_enabled
from drf_api_logger.logger_thread_manager import set_logger_thread, is_thread_running


def start_logger_thread():
    if database_log_enabled():
        from drf_api_logger.insert_log_into_database import InsertLogIntoDatabase

        if not is_thread_running():
            t = InsertLogIntoDatabase()
            t.daemon = True
            t.name = 'insert_log_into_database'
            t.start()
            set_logger_thread(t)
