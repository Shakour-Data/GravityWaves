import unittest
import re
import datetime
from app.services.log_manager import LogManager

log_manager = LogManager()

class TestFrameworkPOC:
    def __init__(self, log_file_path="logs/system.log"):
        self.log_file_path = log_file_path
        self.test_results = {}

    def parse_log_file(self):
        """
        Parses the log file to extract test results.
        Expected log lines format:
        [YYYY-MM-DD HH:MM:SS] Test: <test_name> - Result: PASS/FAIL - Message: <optional>
        """
        pattern = re.compile(r"\\[(.*?)\\] Test: (.*?) - Result: (PASS|FAIL)( - Message: (.*))?")
        with open(self.log_file_path, "r", encoding="utf-8") as f:
            for line in f:
                match = pattern.search(line)
                if match:
                    timestamp, test_name, result, _, message = match.groups()
                    # Normalize test_name by extracting last part after '::' if present (pytest nodeid format)
                    if "::" in test_name:
                        test_name = test_name.split("::")[-1]
                    section = test_name.split()[0]  # Use first word as section
                    if section not in self.test_results:
                        self.test_results[section] = {"PASS": 0, "FAIL": 0, "tests": []}
                    self.test_results[section][result] += 1
                    self.test_results[section]["tests"].append({
                        "name": test_name,
                        "result": result,
                        "message": message or "",
                        "timestamp": timestamp
                    })

    def print_summary(self):
        print("Test Results Summary:")
        for section, results in self.test_results.items():
            total = results["PASS"] + results["FAIL"]
            print(f"Section: {section}")
            print(f"  Total tests: {total}")
            print(f"  Passed: {results['PASS']}")
            print(f"  Failed: {results['FAIL']}")
            print("")

    def run(self):
        self.parse_log_file()
        self.print_summary()

if __name__ == "__main__":
    framework = TestFrameworkPOC()
    framework.run()
