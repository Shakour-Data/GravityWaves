import os
import shutil
import unittest
import subprocess

class TestDocGenerator(unittest.TestCase):
    TEST_CODE_DIR = "Docs/Initial_Documentation/int_docs_tests/sample_code"
    OUTPUT_DIR = "Docs/Initial_Documentation/int_docs_tests/generated_docs"

    @classmethod
    def setUpClass(cls):
        # Create sample code directory and files
        if not os.path.exists(cls.TEST_CODE_DIR):
            os.makedirs(cls.TEST_CODE_DIR)
        sample_file_path = os.path.join(cls.TEST_CODE_DIR, "sample.py")
        with open(sample_file_path, "w", encoding="utf-8") as f:
            f.write("def hello():\n    print('Hello, world!')\n")

        # Ensure output directory is clean
        if os.path.exists(cls.OUTPUT_DIR):
            shutil.rmtree(cls.OUTPUT_DIR)
        os.makedirs(cls.OUTPUT_DIR)

    @classmethod
    def tearDownClass(cls):
        # Clean up test directories
        if os.path.exists(cls.TEST_CODE_DIR):
            shutil.rmtree(cls.TEST_CODE_DIR)
        if os.path.exists(cls.OUTPUT_DIR):
            shutil.rmtree(cls.OUTPUT_DIR)

    def test_doc_generator_runs_and_creates_docs(self):
        # Run the doc_generator.py script with test code directory and output directory
        cmd = [
            "python3",
            "Docs/Initial_Documentation/doc_generator.py",
            self.TEST_CODE_DIR,
            "--output_dir",
            self.OUTPUT_DIR,
        ]
        result = subprocess.run(cmd, capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, msg=f"Script failed: {result.stderr}")

        # Check that documentation file is created
        expected_doc_file = os.path.join(self.OUTPUT_DIR, "sample_doc.md")
        self.assertTrue(os.path.exists(expected_doc_file), "Documentation file not created")

        # Check content of the generated doc file
        with open(expected_doc_file, "r", encoding="utf-8") as f:
            content = f.read()
        self.assertIn("# Documentation for sample.py", content)
        self.assertIn("Generated documentation content for sample.py.", content)

if __name__ == "__main__":
    unittest.main()
