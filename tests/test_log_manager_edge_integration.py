import logging
import pytest
from app.services.log_manager import LogManager

import io

def test_log_manager_error_handling():
    log_manager = LogManager(enable_console_logging=False, enable_file_logging=False)
    log_capture_string = io.StringIO()
    ch = logging.StreamHandler(log_capture_string)
    ch.setLevel(logging.ERROR)
    log_manager.logger.addHandler(ch)

    try:
        raise ValueError("Test error")
    except Exception as e:
        log_manager.log_exception("Exception occurred", e)

    log_manager.logger.removeHandler(ch)
    log_contents = log_capture_string.getvalue()
    log_capture_string.close()

    assert "Exception occurred" in log_contents
    assert "ValueError" in log_contents

def test_log_manager_logging_output():
    log_manager = LogManager(enable_console_logging=False, enable_file_logging=False, log_level="DEBUG")
    log_capture_string = io.StringIO()
    ch = logging.StreamHandler(log_capture_string)
    ch.setLevel(logging.DEBUG)
    log_manager.logger.addHandler(ch)

    log_manager.info("Info message")
    log_manager.debug("Debug message")

    log_manager.logger.removeHandler(ch)
    log_contents = log_capture_string.getvalue()
    log_capture_string.close()

    assert "Info message" in log_contents
    assert "Debug message" in log_contents
