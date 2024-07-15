import os
import sys
import unittest
from unittest.mock import Mock, patch

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from Models.Admin import Admin, FoodItemRepository

class TestAdminMethods(unittest.TestCase):

    def setUp(self):
        self.mock_connection = Mock()
        self.admin = Admin(self.mock_connection)

    def test_add_food_item(self):
        self.admin.food_item_repository.add_food_item = Mock(return_value=1)
        self.admin.notification_service.send_notification_to_all_users = Mock()

        item_name = "Test Item"
        price = 10.99

        result = self.admin.add_food_item(item_name, price)

        self.assertEqual(result, 1)
        self.admin.food_item_repository.add_food_item.assert_called_once_with(item_name, price)
        self.admin.notification_service.send_notification_to_all_users.assert_called_once()

    def test_update_food_item(self):
        self.admin.food_item_repository.update_food_item = Mock()
        
        food_item_id = 1
        item_name = "Updated Item"
        price = 15.99

        self.admin.update_food_item(food_item_id, item_name, price)

        self.admin.food_item_repository.update_food_item.assert_called_once_with(food_item_id, item_name, price)

    def test_delete_food_item(self):
        self.admin.food_item_repository.delete_food_item = Mock()
        
        food_item_id = 1

        self.admin.delete_food_item(food_item_id)

        self.admin.food_item_repository.delete_food_item.assert_called_once_with(food_item_id)

    def test_get_food_items(self):
        mock_food_items = [(1, "Item 1", 10.99), (2, "Item 2", 15.99)]
        self.admin.food_item_repository.get_food_items = Mock(return_value=mock_food_items)

        expected_output = "Menu:\nID: 1, Name: Item 1, Price: 10.99\nID: 2, Name: Item 2, Price: 15.99"

        result = self.admin.get_food_items()

        self.assertEqual(result, expected_output)
        self.admin.food_item_repository.get_food_items.assert_called_once()

    def test_close_connection(self):
        self.admin.food_item_repository.close = Mock()

        self.admin.close_connection()

        self.admin.food_item_repository.close.assert_called_once()

class TestFoodItemRepositoryMethods(unittest.TestCase):

    def setUp(self):
        self.mock_connection = Mock()
        self.repository = FoodItemRepository(self.mock_connection)

    def test_add_food_item(self):
        self.repository.cursor.execute = Mock()
        self.mock_connection.commit = Mock()

        item_name = "Test Item"
        price = 10.99

        self.repository.add_food_item(item_name, price)

        self.repository.cursor.execute.assert_called_once()
        self.mock_connection.commit.assert_called_once()


    def test_delete_food_item(self):
        self.repository.cursor.execute = Mock()
        self.mock_connection.commit = Mock()

        food_item_id = 1

        self.repository.delete_food_item(food_item_id)

        self.repository.cursor.execute.assert_called_once()
        self.mock_connection.commit.assert_called_once()

    def test_get_food_items(self):
        self.repository.cursor.execute = Mock()
        self.repository.cursor.fetchall = Mock(return_value=[(1, "Item 1", 10.99), (2, "Item 2", 15.99)])

        result = self.repository.get_food_items()

        self.assertEqual(len(result), 2)
        self.repository.cursor.execute.assert_called_once()

    def test_close(self):
        self.repository.cursor.close = Mock()
        self.mock_connection.close = Mock()

        self.repository.close()

        self.repository.cursor.close.assert_called_once()
        self.mock_connection.close.assert_called_once()

if __name__ == '__main__':
    unittest.main()
