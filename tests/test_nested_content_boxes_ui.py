import unittest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

class TestNestedContentBoxesUI(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        cls.driver = webdriver.Chrome(options=chrome_options)
        cls.base_url = "http://127.0.0.1:5000/comparative_results"  # Adjust URL as needed

    @classmethod
    def tearDownClass(cls):
        cls.driver.quit()

    def test_navigation_through_levels(self):
        driver = self.driver
        driver.get(self.base_url)
        # Wait up to 5 seconds for breadcrumb element to be present
        breadcrumb = WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.ID, "breadcrumb"))
        )
        current_box = WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.ID, "currentBoxAddress"))
        )

        breadcrumb_text = breadcrumb.text
        current_box_text = current_box.text
        self.assertIn("Level 1", breadcrumb_text)
        self.assertIn("Current Box: Root", current_box_text)

        # Click on first box to go to level 2
        boxes = WebDriverWait(driver, 5).until(
            EC.presence_of_all_elements_located((By.CLASS_NAME, "box"))
        )
        self.assertEqual(len(boxes), 6)
        boxes[0].click()

        breadcrumb = WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.ID, "breadcrumb"))
        )
        current_box = WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.ID, "currentBoxAddress"))
        )
        self.assertIn("Level 2", breadcrumb.text)
        self.assertIn("Current Box: 1", current_box.text)

        # Click on second box to go to level 3
        boxes = WebDriverWait(driver, 5).until(
            EC.presence_of_all_elements_located((By.CLASS_NAME, "box"))
        )
        boxes[1].click()

        breadcrumb = WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.ID, "breadcrumb"))
        )
        current_box = WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.ID, "currentBoxAddress"))
        )
        self.assertIn("Level 3", breadcrumb.text)
        self.assertIn("Current Box: 1 > 2", current_box.text)

        # Test back button functionality
        back_button = WebDriverWait(driver, 5).until(
            EC.element_to_be_clickable((By.ID, "backButton"))
        )
        back_button.click()

        breadcrumb = WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.ID, "breadcrumb"))
        )
        current_box = WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.ID, "currentBoxAddress"))
        )
        self.assertIn("Level 2", breadcrumb.text)
        self.assertIn("Current Box: 1", current_box.text)

        # Navigate back to root
        back_button = WebDriverWait(driver, 5).until(
            EC.element_to_be_clickable((By.ID, "backButton"))
        )
        back_button.click()

        breadcrumb = WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.ID, "breadcrumb"))
        )
        current_box = WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.ID, "currentBoxAddress"))
        )
        self.assertIn("Level 1", breadcrumb.text)
        self.assertIn("Current Box: Root", current_box.text)

if __name__ == "__main__":
    unittest.main()
