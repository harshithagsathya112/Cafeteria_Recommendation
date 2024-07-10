import sys,os
import unittest
from unittest.mock import Mock, patch, call
from datetime import datetime
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from Models.Notification import Notification

class TestNotificationMethods(unittest.TestCase):

    @patch('Models.Notification.execute_query')
    def test_get_unread_notifications(self, mock_execute_query):
        connection = Mock()
        cursor = connection.cursor.return_value
        employee_id = 1
        mock_notifications = [('Notification 1',), ('Notification 2',)]

        cursor.fetchall.return_value = mock_notifications
        mock_execute_query.return_value = None

        notifications = Notification.get_unread_notifications(connection, employee_id)

        self.assertEqual(len(notifications), 2)
        self.assertEqual(notifications[0], 'Notification 1')
        self.assertEqual(notifications[1], 'Notification 2')

        mock_execute_query.assert_called_once()

    @patch('Models.Notification.execute_query')
    def test_send_notification_to_all_users(self, mock_execute_query):
        connection = Mock()
        cursor = connection.cursor.return_value
        message = "Test notification message"
        mock_users = [(1, 'vegetarian'), (2, 'non-vegetarian'), (3, 'vegan')] 

        cursor.fetchall.return_value = mock_users
        mock_execute_query.return_value = None

        Notification.send_notification_to_all_users(connection, message)

        cursor.execute.assert_called()
        insert_queries = [call_args[0][0] for call_args, _ in cursor.execute.call_args_list]
        self.assertEqual(len(insert_queries), len(mock_users))
        self.assertIn(message, insert_queries)

        connection.commit.assert_called_once()

if __name__ == '__main__':
    unittest.main()
