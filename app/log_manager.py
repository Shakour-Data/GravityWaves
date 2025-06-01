# ============================
# Log Manager
# ============================
# Standard Library Imports
# ============================

from enum import Enum
import os
import sys
import datetime
import json
import logging
from logging.handlers import RotatingFileHandler, SMTPHandler
import numpy as np
import pandas as pd
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
import csv
from typing import Dict, Any, Optional, List, Union, Tuple, Callable # Added Callable import
from rich.logging import RichHandler
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
from datetime import datetime as dt_datetime # Renamed to avoid conflict with datetime module
import traceback # Added import for traceback
from io import StringIO # Import StringIO for logging DataFrames

class LogManager:
    """
    The LogManager class for comprehensive log management.
    This class provides logging capabilities to file, console (with Rich), JSON, Slack, and email.
    """
    def __init__(
        self,
        log_file: str = "logs/system.log",
        json_log_file: str = "logs/system.json",
        report_file: str = "reports/market_analysis_report.txt", # Added report file path
        max_log_size: int = 10 * 1024 * 1024,
        backup_count: int = 5,
        slack_token: Optional[str] = None,
        slack_channel: Optional[str] = None,
        smtp_config: Optional[Dict[str, Any]] = None,
        enable_console_logging: bool = True, # New parameter for console logging control
        enable_file_logging: bool = True, # New parameter for file logging control
        enable_json_logging: bool = False, # New parameter for JSON logging control
        enable_slack_logging: bool = False, # New parameter for Slack logging control
        enable_email_logging: bool = False, # New parameter for email logging control
        log_level: str = "INFO", # Default log level
        console_log_level: str = "INFO" # Default console log level
    ):
        """
        Initializes the LogManager with various logging configurations.

        Args:
            log_file (str): Path to the main log file.
            json_log_file (str): Path to the JSON log file.
            report_file (str): Path to the report output file.
            max_log_size (int): Maximum size of the log file before rotation.
            backup_count (int): Number of backup log files to keep.
            slack_token (Optional[str]): Slack API token for Slack notifications.
            slack_channel (Optional[str]): Slack channel to send logs to.
            smtp_config (Optional[Dict[str, Any]]): SMTP configuration for email alerts.
            enable_console_logging (bool): Whether to enable logging to console.
            enable_file_logging (bool): Whether to enable logging to a rotating file.
            enable_json_logging (bool): Whether to enable logging to a JSON file.
            enable_slack_logging (bool): Whether to enable logging to Slack.
            enable_email_logging (bool): Whether to enable logging to email.
            log_level (str): The minimum logging level for file and general handlers (e.g., "INFO", "DEBUG").
            console_log_level (str): The minimum logging level for the console handler.
        """
        self.log_file = log_file
        self.json_log_file = json_log_file
        self.report_file = report_file
        self.max_log_size = max_log_size
        self.backup_count = backup_count
        self.slack_token = slack_token
        self.slack_channel = slack_channel
        self.smtp_config = smtp_config
        self.enable_console_logging = enable_console_logging
        self.enable_file_logging = enable_file_logging
        self.enable_json_logging = enable_json_logging
        self.enable_slack_logging = enable_slack_logging
        self.enable_email_logging = enable_email_logging
        self.log_level = log_level
        self.console_log_level = console_log_level

        self.console = Console(record=True)  # Initialize Rich Console for rich output
        self._setup_logging()
        self.info("LogManager initialized successfully.")

    def _setup_logging(self):
        """
        Sets up the Python logging system with various handlers.
        """
        # Create logs directory if it doesn't exist
        os.makedirs(os.path.dirname(self.log_file), exist_ok=True)
        os.makedirs(os.path.dirname(self.json_log_file), exist_ok=True)
        os.makedirs(os.path.dirname(self.report_file), exist_ok=True) # Ensure reports directory exists

        self.logger = logging.getLogger("MarketAnalysisLogger")
        self.logger.setLevel(self.log_level)
        self.logger.propagate = False # Prevent logs from going to root logger

        # Clear existing handlers to prevent duplicate logs on re-initialization
        if self.logger.handlers:
            for handler in self.logger.handlers[:]:
                self.logger.removeHandler(handler)
                handler.close()

        formatter = logging.Formatter(
            "[%(asctime)s] %(levelname)-8s %(message)s", datefmt="%Y-%m-%d %H:%M:%S"
        )

        # Console Handler (RichHandler)
        if self.enable_console_logging:
            console_handler = RichHandler(
                console=self.console,
                show_time=True,
                show_level=True,
                show_path=False,
                enable_link_path=False,
                rich_tracebacks=True,
                tracebacks_show_locals=True,
                tracebacks_word_wrap=True,
                log_time_format="%m/%d/%y %H:%M:%S"
            )
            console_handler.setLevel(self.console_log_level)
            self.logger.addHandler(console_handler)

        # File Handler (RotatingFileHandler)
        if self.enable_file_logging:
            file_handler = RotatingFileHandler(
                self.log_file,
                maxBytes=self.max_log_size,
                backupCount=self.backup_count,
                encoding="utf-8",
            )
            file_handler.setFormatter(formatter)
            file_handler.setLevel(self.log_level)
            self.logger.addHandler(file_handler)

        # JSON File Handler
        if self.enable_json_logging:
            json_file_handler = logging.FileHandler(self.json_log_file, encoding="utf-8")
            json_file_handler.setFormatter(JsonFormatter())
            json_file_handler.setLevel(self.log_level)
            self.logger.addHandler(json_file_handler)

        # Slack Handler
        if self.enable_slack_logging and self.slack_token and self.slack_channel:
            try:
                slack_client = WebClient(token=self.slack_token)
                slack_handler = SlackHandler(slack_client, self.slack_channel)
                slack_handler.setLevel(logging.ERROR) # Only send ERROR and CRITICAL to Slack
                self.logger.addHandler(slack_handler)
            except Exception as e:
                self.logger.error(f"Failed to set up Slack logger: {e}")

        # Email Handler
        if self.enable_email_logging and self.smtp_config:
            try:
                smtp_handler = SMTPHandler(
                    mailhost=(self.smtp_config["host"], self.smtp_config["port"]),
                    fromaddr=self.smtp_config["from_addr"],
                    toaddrs=self.smtp_config["to_addrs"],
                    subject=self.smtp_config["subject"],
                    credentials=(self.smtp_config["username"], self.smtp_config["password"]),
                    secure=() # Use empty tuple for TLS
                )
                smtp_handler.setFormatter(formatter)
                smtp_handler.setLevel(logging.CRITICAL) # Only send CRITICAL to email
                self.logger.addHandler(smtp_handler)
            except Exception as e:
                self.logger.error(f"Failed to set up SMTP logger: {e}")

    def debug(self, message: str, **kwargs):
        self.logger.debug(message, extra=kwargs)

    def info(self, message: str, **kwargs):
        self.logger.info(message, extra=kwargs)

    def warning(self, message: str, **kwargs):
        self.logger.warning(message, extra=kwargs)

    def error(self, message: str, exc_info: bool = False, **kwargs):
        self.logger.error(message, exc_info=exc_info, extra=kwargs)

    def critical(self, message: str, exc_info: bool = False, **kwargs):
        self.logger.critical(message, exc_info=exc_info, extra=kwargs)

    def log_dataframe(self, df: pd.DataFrame, message: str = "DataFrame content"):
        """Logs a DataFrame's head and info to the console and file."""
        self.info(message)
        self.info(f"DataFrame shape: {df.shape}")
        self.info(f"DataFrame columns: {df.columns.tolist()}")
        self.info(f"DataFrame head:\n{df.head().to_string()}")
        self.info(f"DataFrame info:\n{df.info(buf=StringIO())}") # Capture info to string

    def log_json(self, data: Dict[str, Any], message: str = "JSON data"):
        """Logs a dictionary as a JSON string."""
        self.info(message)
        self.info(json.dumps(data, indent=2))

    def log_exception(self, message: str, exc: Exception):
        """Logs an exception with traceback."""
        self.error(message, exc_info=True)


class JsonFormatter(logging.Formatter):
    """
    A custom formatter to output log records as JSON strings.
    """
    def format(self, record):
        log_record = {
            "timestamp": dt_datetime.fromtimestamp(record.created).isoformat(),
            "level": record.levelname,
            "message": record.getMessage(),
        }
        if record.exc_info:
            log_record["exc_info"] = self.formatException(record.exc_info)
        if record.stack_info:
            log_record["stack_info"] = self.formatStack(record.stack_info)
        # Add any extra attributes passed to the log record
        for key, value in record.__dict__.items():
            if key not in ['name', 'levelname', 'pathname', 'lineno', 'asctime',
                           'message', 'args', 'exc_info', 'exc_text', 'stack_info',
                           'filename', 'funcName', 'created', 'msecs', 'relativeCreated',
                           'thread', 'threadName', 'processName', 'process', 'module',
                           '_log_record_fields', 'levelno', 'msg', 'raw_message']: # Exclude standard attrs
                if not key.startswith('_'): # Exclude internal attributes
                    try:
                        # Attempt to serialize complex objects, fall back to string representation
                        json.dumps(value)
                        log_record[key] = value
                    except (TypeError, OverflowError):
                        log_record[key] = str(value)
        return json.dumps(log_record, ensure_ascii=False)


class SlackHandler(logging.Handler):
    """
    A custom logging handler to send messages to Slack.
    """
    def __init__(self, client: WebClient, channel: str):
        super().__init__()
        self.client = client
        self.channel = channel

    def emit(self, record):
        log_entry = self.format(record)
        try:
            self.client.chat_postMessage(channel=self.channel, text=log_entry)
        except SlackApiError as e:
            print(f"Error sending Slack message: {e.response['error']}", file=sys.stderr)


class ConsolePrinter:
    """
    A utility class for printing formatted output to the console using Rich.
    """
    def __init__(self):
        self.console = Console()

    def print_panel(self, title: str, content: Union[str, Text], style: str = "bold green"):
        """Prints content within a Rich Panel."""
        if not isinstance(content, Text):
            content = Text(str(content))
        self.console.print(Panel(content, title=title, border_style=style, expand=True))

    def print_section_header(self, title: str, description: str = ""):
        """Prints a formatted section header with an optional description."""
        self.console.print(self._get_separator_str())
        self.console.print(Text(title, style="bold blue", justify="center"))
        if description:
            self.console.print(Text(description, style="italic dim", justify="center"))
        self.console.print(self._get_separator_str())

    def print_separator(self, length: int = 80, char: str = '-'):
        """Prints a separator line to the console."""
        self.console.print(self._get_separator_str(length, char))

    def _get_section_header_str(self, title: str, description: str) -> str:
        """
        Returns a formatted section header string.
        Note: This method is primarily for internal string formatting if needed elsewhere.
        For direct console printing, use print_section_header.
        """
        header_text = Text(title, style="bold blue", justify="center")
        desc_text = Text(description, style="italic dim", justify="center") if description else Text("")
        
        combined_text = Text("")
        combined_text.append("\n")
        combined_text.append(header_text)
        combined_text.append("\n")
        combined_text.append(desc_text)
        combined_text.append("\n")
        return combined_text.plain # Return plain string for f-string, or return Text object if print can handle it.

    def _get_table_str(self, title: str, headers: List[str], data: List[List[Any]], title_style: str = "", header_style: str = "") -> str:
        """Returns a formatted table string."""
        table = Table(title=Text(title, style=title_style))
        for header in headers:
            table.add_column(Text(header, style=header_style))
        for row in data:
            table.add_row(*[str(item) for item in row])
        # Again, this returns a Rich Table object, not a plain string.
        # ReportMaker's _format_table handles plain string conversion.
        return str(table) # Fallback for this helper

    def print_table(self, title: str, headers: List[str], data: List[List[Any]], title_style: str = "bold green", header_style: str = "bold yellow"):
        """Prints a formatted table to the console."""
        table = Table(title=Text(title, style=title_style))
        for header in headers:
            table.add_column(Text(header, style=header_style))
        for row in data:
            table.add_row(*[str(item) for item in row])
        self.console.print(table)

    def _get_separator_str(self, length: int = 80, char: str = '-') -> str:
        """Returns a formatted separator string."""
        return char * length
