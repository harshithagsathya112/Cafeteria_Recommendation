import unittest
from unittest.mock import patch
import logging
import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from Utils.Logger import log_activity 

class TestLogActivity(unittest.TestCase):
    @patch('logging.info')
    def test_log_activity(self, mock_logging_info):
        test_message = "hiiiiiiiiii_testinggggggggggg"
        log_activity(test_message)
        mock_logging_info.assert_called_once_with(test_message)

    def test_log_file(self):
        log_file_path = 'src/Data/user_activity.log'
        for handler in logging.root.handlers[:]:
            logging.root.removeHandler(handler)
            handler.close()

        if os.path.exists(log_file_path):
            os.remove(log_file_path)

        test_message = "hiiiiiiiiii_testinggggggggggg"
        log_activity(test_message)

        with open(log_file_path, 'r') as log_file:
            log_contents = log_file.read()
            self.assertIn(test_message, log_contents)

if __name__ == "__main__":
    unittest.main()
