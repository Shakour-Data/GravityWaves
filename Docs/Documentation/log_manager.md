# log_manager.py Documentation

## Overview
The `log_manager.py` module provides the `LogManager` class for comprehensive logging management. It supports logging to multiple outputs including console (with Rich formatting), rotating log files, JSON files, Slack channels, and email alerts. The module also includes helper classes for JSON formatting, Slack logging, and console printing.

---

## LogManager Class

### Description
The `LogManager` class centralizes logging configuration and usage for the application. It allows flexible enabling/disabling of various logging outputs and manages log rotation, formatting, and external notifications.

### Initialization
- Configurable log file paths, sizes, and backup counts.
- Optional Slack and SMTP configurations for notifications.
- Control over which logging outputs are enabled.
- Separate log levels for console and file logging.

### Key Methods
- `_setup_logging()`: Configures Python logging with handlers for console, file, JSON, Slack, and email.
- `debug()`, `info()`, `warning()`, `error()`, `critical()`: Logging methods for different severity levels.
- `log_dataframe()`: Logs Pandas DataFrame content and info.
- `log_json()`: Logs JSON data.
- `log_exception()`: Logs exceptions with traceback.

---

## Helper Classes

### JsonFormatter
Custom logging formatter that outputs log records as JSON strings, including timestamps, levels, messages, and exception info.

### SlackHandler
Custom logging handler that sends log messages to a configured Slack channel using the Slack WebClient.

### ConsolePrinter
Utility class for printing formatted output to the console using Rich, including panels, section headers, tables, and separators.

---

## Usage Example

```python
log_manager = LogManager(enable_console_logging=True, enable_file_logging=True)
log_manager.info("Application started")
log_manager.log_dataframe(df, "Sample DataFrame")
try:
    # some code
except Exception as e:
    log_manager.log_exception("Error occurred", e)
```

---

## Diagrams

- **Class Diagram:** Shows LogManager and helper classes with their relationships.
- **Sequence Diagram:** Illustrates logging flow from application code through LogManager to various outputs.

---

This documentation provides a detailed understanding of the logging system and its usage within the application.
