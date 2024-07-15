import unittest
import sys, os
from unittest.mock import Mock, patch
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from Models.UserLogin import User

class TestUser(unittest.TestCase):

    @patch('Models.UserLogin.execute_read_query')
    def test_get_role_from_employeeid(self, mock_execute_read_query):
        mock_connection = Mock()
        mock_execute_read_query.return_value = [('Admin',)]
        role = User.get_role_from_employeeid('123456', mock_connection)
        self.assertEqual(role, 'Admin')
        mock_execute_read_query.assert_called_once()

    @patch('Models.UserLogin.execute_read_query')
    def test_verify_employee_valid(self, mock_execute_read_query):
        mock_connection = Mock()
        mock_execute_read_query.return_value = [('Admin',)]

        result, employeeid = User.verify_employee('John Doe', '123456', mock_connection)

        self.assertEqual(result, 'Admin')
        self.assertEqual(employeeid, '123456')
        mock_execute_read_query.assert_called()

    @patch('Models.UserLogin.execute_read_query')
    def test_verify_employee_invalid(self, mock_execute_read_query):
        mock_connection = Mock()
        mock_execute_read_query.return_value = []

        result, employeeid = User.verify_employee('Unknown User', '999999', mock_connection)

        self.assertIsNone(result)
        self.assertIsNone(employeeid)
        mock_execute_read_query.assert_called()

if __name__ == '__main__':
    unittest.main()

