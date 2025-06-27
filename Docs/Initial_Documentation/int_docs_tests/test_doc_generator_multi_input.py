import os
import shutil
import unittest
import subprocess

class TestDocGeneratorMultiInput(unittest.TestCase):
    TEST_INPUTS = [
        "app/services",
        "templates",
        "app.py"
    ]
    OUTPUT_DIR = "Docs/Initial_Documentation/int_docs_tests/generated_docs_multi"

    @classmethod
    def setUpClass(cls):
        # Ensure output directory is clean
        if os.path.exists(cls.OUTPUT_DIR):
            shutil.rmtree(cls.OUTPUT_DIR)
        os.makedirs(cls.OUTPUT_DIR)

    @classmethod
    def tearDownClass(cls):
        # Clean up output directory after tests
        if os.path.exists(cls.OUTPUT_DIR):
            shutil.rmtree(cls.OUTPUT_DIR)

    def test_doc_generator_with_multiple_inputs(self):
        # Run the doc_generator.py script with multiple input paths and output directory
        cmd = [
            "python3",
            "Docs/Initial_Documentation/doc_generator.py",
            *self.TEST_INPUTS,
            "--output_dir",
            self.OUTPUT_DIR,
        ]
        result = subprocess.run(cmd, capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, msg=f"Script failed: {result.stderr}")

        # Check that documentation files are created for some expected files
        expected_doc_files = [
            "app_doc.md",
            "assistant_analysis_doc.md",  # example file from app/services
            "index_doc.md",  # example HTML file from templates
        ]
        found_files = os.listdir(self.OUTPUT_DIR)
        for expected_file in expected_doc_files:
            self.assertIn(expected_file, found_files, f"Expected documentation file {expected_file} not found")

if __name__ == "__main__":
    unittest.main()
