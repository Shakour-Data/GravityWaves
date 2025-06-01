import logging
import pytest
from app.services.log_manager import LogManager

def test_log_manager_initialization():
    log_manager = LogManager(enable_console_logging=False, enable_file_logging=False, enable_json_logging=False, enable_slack_logging=False, enable_email_logging=False)
    assert log_manager.logger is not None

import io

def test_logging_methods():
    log_manager = LogManager(enable_console_logging=False, enable_file_logging=False, log_level="DEBUG")
    log_capture_string = io.StringIO()
    ch = logging.StreamHandler(log_capture_string)
    ch.setLevel(logging.DEBUG)
    log_manager.logger.addHandler(ch)

    log_manager.info("Info message")
    log_manager.debug("Debug message")
    log_manager.warning("Warning message")
    log_manager.error("Error message")
    log_manager.critical("Critical message")

    log_manager.logger.removeHandler(ch)
    log_contents = log_capture_string.getvalue()
    log_capture_string.close()

    assert "Info message" in log_contents
    assert "Debug message" in log_contents
    assert "Warning message" in log_contents
    assert "Error message" in log_contents
    assert "Critical message" in log_contents
