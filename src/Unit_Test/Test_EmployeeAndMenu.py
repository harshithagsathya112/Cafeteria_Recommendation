import os
import sys
import unittest
from unittest.mock import Mock, patch
from datetime import datetime, timedelta
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from Models.Employee import Employee
from Models.Notification import Notification
from Models.Menu import MenuManager

class TestEmployeeMethods(unittest.TestCase):

    def setUp(self):
        self.connection = Mock()
        self.cursor = self.connection.cursor.return_value
        self.cursor.fetchone.return_value = (1,)

        self.mock_today = datetime.now()
        self.mock_yesterday = self.mock_today - timedelta(days=1)
        self.mock_today_str = self.mock_today.strftime('%Y-%m-%d')
        self.mock_yesterday_str = self.mock_yesterday.strftime('%Y-%m-%d')

        self.mock_menu_manager = Mock()
        self.mock_menu_manager.sort_menu_items.return_value = [('item1', 'price1', 'mealtype1')]
        self.mock_menu_manager.format_menu_output.return_value = "Mock menu output"

        patcher = patch.multiple('Models.Employee',
                                 MenuManager=self.mock_menu_manager,
                                 execute_read_query=Mock())
        patcher.start()
        self.addCleanup(patcher.stop)

    def test_get_role(self):
        employee = Employee(1)
        role_name = "Mock Role"
        self.cursor.fetchone.return_value = (role_name,)

        with patch('Models.Employee.User.get_role_from_employeeid', return_value=role_name):
            result = employee.get_role(self.connection)
            self.assertEqual(result, role_name)

    def test_select_food_item(self):
        employee = Employee(1)
        self.cursor.fetchone.side_effect = [(1,), None]
        self.cursor.fetchall.return_value = [('FoodItemID1', 'ItemName1', 'Price1', 'MealType1')]

        result = employee.select_food_item(self.connection, employee_id=1, food_item_id='FoodItemID1')
        self.assertIn("selection has been recorded", result)

    def test_give_feedback(self):
        employee = Employee(1)
        self.cursor.fetchone.return_value = (1,)

        result = employee.give_feedback(self.connection, 1, 'FoodItemID1', 'Mock comment', 5)
        self.assertIn("Feedback submitted successfully", result)

    def test_fetch_pending_questions(self):
        employee = Employee(1)
        self.cursor.fetchone.return_value = (1,)
        self.cursor.fetchall.return_value = [(1, 'Mock Question')]

        result = employee.fetch_pending_questions(self.connection)
        self.assertIn("Pending Survey Questions", result)


class TestMenuManagerMethods(unittest.TestCase):

    def setUp(self):
        self.connection = Mock()
        self.cursor = self.connection.cursor.return_value

    def test_fetch_user_preference(self):
        manager = MenuManager(self.connection)
        self.cursor.fetchone.side_effect = [('User',), ('mock_pref', 'mock_spice', 'mock_cuisine', 'mock_tooth')]

        role, details = manager.fetch_user_preference(1)
        self.assertEqual(role, 'User')
        self.assertEqual(details, ('mock_pref', 'mock_spice', 'mock_cuisine', 'mock_tooth'))

    def test_roll_out_menu(self):
        manager = MenuManager(self.connection)
        self.cursor.fetchone.return_value = ('Mock Item',)
        
        with patch.object(manager, 'notify_users_about_menu', return_value=None):
            result = manager.roll_out_menu('Lunch', 1)
            self.assertIn("Menu rolled out for the next day.", result)

    def test_view_rolled_out_menu_for_today(self):
        manager = MenuManager(self.connection)
        self.cursor.fetchone.side_effect = [
            ('User',), 
            ('mock_pref', 'mock_spice', 'mock_cuisine', 'mock_tooth'), 
            ('item1', 'price1', 'mealtype1', 'dietary', 'spice', 'cuisine', 'sweet')
        ]
        self.cursor.fetchall.return_value = [
            ('item1', 'price1', 'mealtype1', 'dietary', 'spice', 'cuisine', 'sweet')
        ]

        with patch.object(manager, 'sort_menu_items', return_value=[('item1', 'price1', 'mealtype1')]), \
             patch.object(manager, 'format_menu_output', return_value="Mock menu output"):
            result = manager.view_rolled_out_menu_for_today(1)
            self.assertEqual(result, "Mock menu output")

    def test_update_menu_and_availability_status(self):
        manager = MenuManager(self.connection)
        self.cursor.fetchone.side_effect = [(0,), (1,), ('Mock Item',)]
        self.cursor.fetchall.return_value = [(1,)]

        with patch.object(Notification, 'send_notification_to_all_users', return_value=None):
            result = manager.update_menu_and_availability_status('Lunch', 1)
            self.assertIn("Food item is added for today's menu.", result)

    def test_sort_menu_items(self):
        manager = MenuManager(self.connection)
        menu_items = [
            (1, 'item1', 'price1', 'mealtype1', 'pref1', 'spicy', 'cuisine1', 0),
            (2, 'item2', 'price2', 'mealtype2', 'pref2', 'mild', 'cuisine2', 1)
        ]
        sorted_items = manager.sort_menu_items(menu_items, 'pref1', 'spicy', 'cuisine1', True)
        self.assertEqual(sorted_items[0][1], 'item1')

    def test_format_menu_output(self):
        manager = MenuManager(self.connection)
        menu_items = [
            (1, 'item1', 'price1', 'mealtype1'),
            (2, 'item2', 'price2', 'mealtype2')
        ]
        output = manager.format_menu_output(menu_items)
        self.assertIn("ID: 1, Name: item1, Price: price1, Meal Type: mealtype1", output)
        self.assertIn("ID: 2, Name: item2, Price: price2, Meal Type: mealtype2", output)

if __name__ == '__main__':
    unittest.main()
