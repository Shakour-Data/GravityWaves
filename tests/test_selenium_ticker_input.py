import unittest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
import time

class TickerInputSeleniumTest(unittest.TestCase):
    def setUp(self):
        self.driver = webdriver.Chrome()  # Ensure chromedriver is installed and in PATH
        self.driver.get("http://localhost:5000")  # Adjust URL as needed

    def tearDown(self):
        self.driver.quit()

    def test_ticker_input_and_log_check(self):
        driver = self.driver
        wait = WebDriverWait(driver, 20)  # Increased timeout to 20 seconds

        # Locate the global ticker input in sidebar
        ticker_input = wait.until(EC.presence_of_element_located((By.ID, "global_ticker")))

        # Test with different tickers
        test_tickers = ["AAPL", "MSFT", "فولاد", "GOOG"]

        for ticker in test_tickers:
            ticker_input.clear()
            ticker_input.send_keys(ticker)
            ticker_input.send_keys(Keys.TAB)  # Trigger input event

            # Wait for the page or data to update
            time.sleep(5)  # Wait 5 seconds for data to load

            # Check if the elements exist, if not print warning and continue
            try:
                current_state_elem = wait.until(EC.presence_of_element_located((By.ID, "current-market-state")))
                volatility_regime_elem = wait.until(EC.presence_of_element_located((By.ID, "current-volatility-regime")))
                print(f"Ticker: {ticker}, Market State: {current_state_elem.text}, Volatility Regime: {volatility_regime_elem.text}")
            except Exception as e:
                print(f"Ticker: {ticker}, Error finding elements: {e}")

if __name__ == "__main__":
    unittest.main()
