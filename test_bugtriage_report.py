import unittest
from unittest.mock import patch
from io import StringIO
import sys

# Import the classes and functions from the main script
from Kestrel_JMergedCode import BugtriageReport, extract_url_from_text

class TestBugtriageReport(unittest.TestCase):
    @patch('Kestrel_JMergedCode.readPropertyValue')
    def test_construct_table(self, mock_readPropertyValue):
        # Mock the return value of readPropertyValue
        mock_readPropertyValue.return_value = "mocked_value"

        # Create an instance of BugtriageReport
        report = BugtriageReport("reportid", "type", "result_text", "url")
        # Call the method you want to test
        table = report.construct_table()

        # Assertions
        self.assertIsInstance(table, str)  # Ensure the output is a string
        # Add more assertions as needed

    def test_extract_url_from_text(self):
        # Test if extract_url_from_text() correctly extracts URL from text
        text_with_url = "Description: [https://wisdom/sample-url]"
        self.assertEqual(extract_url_from_text(text_with_url), "https://wisdom/sample-url")

        text_without_url = "Description: No URL in this text"
        self.assertIsNone(extract_url_from_text(text_without_url))

if __name__ == '__main__':
    unittest.main()
