import os
import subprocess
import datetime
import re
import signal
import time
import pytest
from app.services.log_manager import LogManager

def run_tests_poc(tests_dir='tests', poc_log_dir='logs', human_log_file='logs/human_readable.log'):
    # Initialize LogManager for human-readable logs
    log_manager = LogManager(log_file=human_log_file, enable_console_logging=True, enable_file_logging=True)

    # Generate timestamped POC log filename
    timestamp_str = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
    poc_log_file = os.path.join(poc_log_dir, f'system_{timestamp_str}.log')

    # Clear previous human-readable log file
    if os.path.exists(human_log_file):
        os.remove(human_log_file)

    # Start the Flask app in background, redirecting output to human-readable log
    run_app_cmd = ['./run_app.sh']
    app_log_file = open(human_log_file, 'a', encoding='utf-8')
    app_process = subprocess.Popen(run_app_cmd, stdout=app_log_file, stderr=app_log_file, preexec_fn=os.setsid)
    log_manager.info(f'Started Flask app with PID {app_process.pid}')
    print(f'Started Flask app with PID {app_process.pid}')
    # Wait a few seconds for the app to start
    time.sleep(5)

    # Discover test files
    test_files = sorted(
        f for f in os.listdir(tests_dir)
        if f.startswith('test_') and f.endswith('.py')
    )

    # Optional mapping of test files to system parts for log headers
    test_file_descriptions = {
        'test_selenium_ui.py': 'Selenium UI Tests',
        'test_internal_server_errors.py': 'Internal Server Error Tests',
        'test_cache_manager.py': 'Cache Manager Tests',
        'test_market_analysis_system.py': 'Market Analysis System Tests',
        'test_market_data_fetcher.py': 'Market Data Fetcher Tests',
        'test_optimization_engine.py': 'Optimization Engine Tests',
        'test_indicator_calculator.py': 'Indicator Calculator Tests',
        'test_log_manager.py': 'Log Manager Tests',
        'test_additional_api_endpoints.py': 'Additional API Endpoints Tests',
        'test_comprehensive.py': 'Comprehensive System Tests',
        'test_framework_poc.py': 'Framework POC Tests',
        'test_indicator_calculator_edge_integration.py': 'Indicator Calculator Edge Integration Tests',
        'test_log_manager_edge_integration.py': 'Log Manager Edge Integration Tests',
        'test_market_analysis_system_edge_integration.py': 'Market Analysis System Edge Integration Tests',
        'test_market_data_fetcher_edge_integration.py': 'Market Data Fetcher Edge Integration Tests',
        'test_optimization_engine_edge_integration.py': 'Optimization Engine Edge Integration Tests',
        'test_selenium_ticker_input.py': 'Selenium Ticker Input Tests',
        'test_app.py': 'App Tests',
    }

    for test_file in test_files:
        test_path = os.path.join(tests_dir, test_file)
        description = test_file_descriptions.get(test_file, 'General Tests')

        # Write header for this test file in POC log
        with open(poc_log_file, 'a', encoding='utf-8') as log_f:
            header = f"\\n=== Running {description} ({test_file}) ===\\n"
            log_f.write(header)
        log_manager.info(f'Running tests in {test_path} ({description})...')
        print(f'Running tests in {test_path} ({description})...')

        # Run pytest with detailed output and JSON report
        env = os.environ.copy()
        env['PYTHONPATH'] = os.getcwd()
        result = subprocess.run(
            ['pytest', test_path, '--tb=short', '-q', '--disable-warnings', '--json-report', '--json-report-file=report.json'],
            capture_output=True,
            text=True,
            env=env
        )

        # Parse pytest JSON report for test results and summary
        if os.path.exists('report.json'):
            import json
            with open('report.json', 'r', encoding='utf-8') as f:
                report = json.load(f)
            total_tests = len(report.get('tests', []))
            passed_tests = sum(1 for t in report.get('tests', []) if t.get('outcome') == 'passed')
            failed_tests = sum(1 for t in report.get('tests', []) if t.get('outcome') == 'failed')

            with open(poc_log_file, 'a', encoding='utf-8') as log_f:
                summary = f"Summary: Total={total_tests}, Passed={passed_tests}, Failed={failed_tests}\\n"
                log_f.write(summary)
                for test in report.get('tests', []):
                    test_name = test.get('nodeid', 'unknown test')
                    outcome = test.get('outcome', 'unknown').upper()
                    message = ''
                    if outcome == 'FAILED':
                        # Extract failure message if available
                        message = test.get('longrepr', '')
                        # Clean message to single line
                        message = re.sub(r'\\s+', ' ', message).strip()
                    timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    log_line = f"[{timestamp}] Test: {test_name} - Result: {outcome} - Message: {message}\\n"
                    log_f.write(log_line)
                    # Also log human-readable message
                    human_msg = f"Test '{test_name}' result: {outcome}. {message}"
                    log_manager.info(human_msg)
            os.remove('report.json')
        else:
            # Fallback: log overall result
            timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            outcome = 'PASS' if result.returncode == 0 else 'FAIL'
            with open(poc_log_file, 'a', encoding='utf-8') as log_f:
                log_line = f"[{timestamp}] Test: {test_path} - Result: {outcome} - Message: \\n"
                log_f.write(log_line)
            human_msg = f"Test file '{test_path}' result: {outcome}."
            log_manager.info(human_msg)

        if result.returncode != 0:
            log_manager.warning(f'Tests failed in {test_path}. Continuing with next tests.')
            print(f'Tests failed in {test_path}. Continuing with next tests.')
        else:
            log_manager.info(f'Tests passed in {test_path}.')
            print(f'Tests passed in {test_path}.')

    # Stop the Flask app
    try:
        os.killpg(os.getpgid(app_process.pid), signal.SIGTERM)
        log_manager.info(f'Stopped Flask app with PID {app_process.pid}')
        print(f'Stopped Flask app with PID {app_process.pid}')
    except Exception as e:
        log_manager.error(f'Error stopping Flask app: {e}')
        print(f'Error stopping Flask app: {e}')

    log_manager.info(f'Test run complete. See {poc_log_file} for details.')
    print(f'Test run complete. See {poc_log_file} for details.')

if __name__ == '__main__':
    run_tests_poc()
