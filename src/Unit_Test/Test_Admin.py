import unittest
from unittest.mock import patch
import os
import sys
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(project_root)
from Models.Admin import Admin, FoodItemRepository  

class TestFoodItemRepository(unittest.TestCase):

    @patch('Models.Admin.create_connection')
    def setUp(self, MockCreateConnection):
        self.mock_conn = MockCreateConnection.return_value
        self.mock_cursor = self.mock_conn.cursor.return_value
        self.repo = FoodItemRepository(self.mock_conn)

    def test_add_food_item(self):
        self.mock_cursor.lastrowid = 1
        food_item_id = self.repo.add_food_item("Pizza", 10.99)
        self.assertEqual(food_item_id, 1)
        self.mock_cursor.execute.assert_called_once()
        self.mock_conn.commit.assert_called_once()

    def test_update_food_item(self):
        self.repo.update_food_item(1, item_name="Burger", price=5.99)
        self.mock_cursor.execute.assert_any_call("SET SQL_SAFE_UPDATES = 0;")
        self.mock_cursor.execute.assert_any_call("SET SQL_SAFE_UPDATES = 1;")
        self.mock_conn.commit.assert_called_once()

    def test_delete_food_item(self):
        self.repo.delete_food_item(1)
        self.mock_cursor.execute.assert_called_once_with("DELETE FROM fooditem_main WHERE LookupID = %s", (1,))
        self.mock_conn.commit.assert_called_once()

    def test_get_food_items(self):
        self.mock_cursor.fetchall.return_value = [(1, "Pizza", 10.99)]
        food_items = self.repo.get_food_items()
        self.assertEqual(food_items, [(1, "Pizza", 10.99)])

    def test_close(self):
        self.repo.close()
        self.mock_cursor.close.assert_called_once()
        self.mock_conn.close.assert_called_once()

class TestAdmin(unittest.TestCase):

    @patch('Models.Admin.create_connection')
    @patch('Models.Admin.Notification')
    def setUp(self, MockNotification, MockCreateConnection):
        self.mock_conn = MockCreateConnection.return_value
        self.mock_cursor = self.mock_conn.cursor.return_value
        self.mock_notification = MockNotification.return_value
        self.Admin = Admin()

    def test_add_food_item(self):
        self.mock_cursor.lastrowid = 1
        food_item_id = self.Admin.add_food_item("Pizza", 10.99)
        self.assertEqual(food_item_id, 1)
        self.mock_cursor.execute.assert_called_once()
        self.mock_conn.commit.assert_called_once()
        self.mock_notification.insert_notification_for_all_users.assert_called_once()

    def test_update_food_item(self):
        self.Admin.update_food_item(1, item_name="Burger", price=5.99)
        self.mock_cursor.execute.assert_any_call("SET SQL_SAFE_UPDATES = 0;")
        self.mock_cursor.execute.assert_any_call("SET SQL_SAFE_UPDATES = 1;")
        self.mock_conn.commit.assert_called_once()

    def test_delete_food_item(self):
        self.Admin.delete_food_item(1)
        self.mock_cursor.execute.assert_called_once_with("DELETE FROM fooditem_main WHERE LookupID = %s", (1,))
        self.mock_conn.commit.assert_called_once()

    def test_get_food_items(self):
        self.mock_cursor.fetchall.return_value = [(1, "Pizza", 10.99)]
        menu = self.Admin.get_food_items()
        self.assertIn("Pizza", menu)

    def test_close_connection(self):
        self.Admin.close_connection()
        self.mock_cursor.close.assert_called_once()
        self.mock_conn.close.assert_called_once()

if __name__ == '__main__':
    unittest.main()
