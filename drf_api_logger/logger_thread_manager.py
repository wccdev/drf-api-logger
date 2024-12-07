import threading

_LOGGER_THREAD = None
LOG_THREAD_NAME = 'insert_log_into_database'

def get_logger_thread():
    global _LOGGER_THREAD
    return _LOGGER_THREAD

def set_logger_thread(thread):
    global _LOGGER_THREAD
    _LOGGER_THREAD = thread

def is_thread_running():
    return any(t.name == LOG_THREAD_NAME for t in threading.enumerate())
