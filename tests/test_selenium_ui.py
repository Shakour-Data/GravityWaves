import unittest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options

class TestWebUI(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        import subprocess
        import time
        import socket
        import urllib.request

        # Start the Flask server before running tests on port 5000 (changed from 5001)
        cls.server_process = subprocess.Popen(["python3", "app.py", "--port", "5000"])

        # Wait for the server to be accessible with retries
        cls.base_url = "http://localhost:5000"
        max_retries = 10
        for i in range(max_retries):
            try:
                with urllib.request.urlopen(cls.base_url) as response:
                    if response.status == 200:
                        break
            except Exception:
                time.sleep(1)
        else:
            raise RuntimeError(f"Server not accessible at {cls.base_url} after {max_retries} retries")

        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        cls.driver = webdriver.Chrome(options=chrome_options)
        cls.driver.implicitly_wait(5)

    @classmethod
    def tearDownClass(cls):
        cls.driver.quit()
        # Terminate the Flask server after tests
        cls.server_process.terminate()

    def test_index_page_links(self):
        self.driver.get(self.base_url + "/")
        # Check page title
        self.assertIn("Stock Market Analysis", self.driver.title)

        # Check presence of links to analysis pages
        forecast_link = self.driver.find_element(By.LINK_TEXT, "Forecast Analysis")
        self.assertIsNotNone(forecast_link)
        market_status_link = self.driver.find_element(By.LINK_TEXT, "Market Status Analysis")
        self.assertIsNotNone(market_status_link)

    def test_forecast_analysis_page(self):
        self.driver.get(self.base_url + "/forecast_analysis")
        self.assertIn("Forecast Analysis", self.driver.page_source)
        # Wait for form elements
        WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.ID, "ticker"))
        )
        WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.ID, "analysis_date"))
        )
        WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.ID, "timeframe"))
        )
        WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.ID, "prediction_horizons"))
        )
        self.assertTrue(self.driver.find_element(By.ID, "ticker"))
        self.assertTrue(self.driver.find_element(By.ID, "analysis_date"))
        self.assertTrue(self.driver.find_element(By.ID, "timeframe"))
        self.assertTrue(self.driver.find_element(By.ID, "prediction_horizons"))

    def test_market_status_analysis_page(self):
        self.driver.get(self.base_url + "/market_status_analysis")
        self.assertIn("Market Status Analysis", self.driver.page_source)
        # Wait for page to load fully
        WebDriverWait(self.driver, 20).until(
            EC.presence_of_element_located((By.ID, "current-market-state"))
        )
        # Check for ticker input presence (if any)
        ticker_elements = self.driver.find_elements(By.ID, "ticker")
        if ticker_elements:
            self.assertTrue(ticker_elements[0].is_displayed())
        # Check for analysis_date input presence (if any)
        analysis_date_elements = self.driver.find_elements(By.ID, "analysis_date")
        if analysis_date_elements:
            self.assertTrue(analysis_date_elements[0].is_displayed())
        # Check for timeframe input presence (if any)
        timeframe_elements = self.driver.find_elements(By.ID, "timeframe")
        if timeframe_elements:
            self.assertTrue(timeframe_elements[0].is_displayed())

    def test_run_forecast_analysis_form(self):
        self.driver.get(self.base_url + "/forecast_analysis")
        ticker_input = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.ID, "ticker"))
        )
        analysis_date_input = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.ID, "analysis_date"))
        )
        prediction_horizons_input = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.ID, "prediction_horizons"))
        )
        submit_button = WebDriverWait(self.driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "button[type='submit']"))
        )

        ticker_input.clear()
        ticker_input.send_keys("AAPL")
        analysis_date_input.clear()
        analysis_date_input.send_keys("2023-01-01")
        prediction_horizons_input.clear()
        prediction_horizons_input.send_keys("1,5,10")
        submit_button.click()

        # Wait for results to appear
        results_div = WebDriverWait(self.driver, 20).until(
            EC.presence_of_element_located((By.ID, "results"))
        )
        self.assertIn("Forecast Analysis Results", results_div.text)

if __name__ == "__main__":
    unittest.main()
