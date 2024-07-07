import unittest
from unittest.mock import MagicMock, patch
import os,sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from Models.chef import Chef  
from Models.Menu import MenuManager

class TestChef(unittest.TestCase):

    def setUp(self):
        self.connection = MagicMock()
        self.chef = Chef(user_id=1, employee_id=123, name="Test Chef", role_id=2, password="password", connection=self.connection)

    def test_fetch_food_items(self):
        cursor_mock = MagicMock()
        self.connection.cursor.return_value = cursor_mock
        cursor_mock.fetchall.return_value = [
            (1, "Pizza", 12.99, True),
            (2, "Burger", 8.99, False)
        ]

        result = self.chef.fetch_food_items(self.connection)
        expected_result = "Menu:\nID: 1, Name: Pizza, Price: 12.99, Available: True\nID: 2, Name: Burger, Price: 8.99, Available: False"
        self.assertEqual(result, expected_result)

    @patch.object(MenuManager, 'roll_out_menu')
    def test_roll_out_menu(self, mock_roll_out_menu):
        mock_roll_out_menu.return_value = "Menu rolled out for the next day."
        result = self.chef.roll_out_menu("Lunch", 1)
        self.assertEqual(result, "Menu rolled out for the next day.")
        mock_roll_out_menu.assert_called_once_with("Lunch", 1)

    def test_view_feedback(self):
        cursor_mock = MagicMock()
        self.connection.cursor.return_value = cursor_mock
        cursor_mock.fetchall.return_value = [
            (1, 1, "Great food!", 5, "2024-07-07", 1),
            (2, 2, "Could be better.", 3, "2024-07-06", 2)
        ]

        result = self.chef.view_feedback(self.connection)
        expected_result = "Feedback:\nFeedback ID: 1, User ID: 1, Comment: Great food!, Rating: 5, Date: 2024-07-07, Food Item ID: 1\nFeedback ID: 2, User ID: 2, Comment: Could be better., Rating: 3, Date: 2024-07-06, Food Item ID: 2\n"
        self.assertEqual(result, expected_result)

    def test_generate_report(self):
        cursor_mock = MagicMock()
        self.connection.cursor.return_value = cursor_mock
        cursor_mock.fetchall.return_value = [
            (1, 4.5, 10),
            (2, 3.7, 5)
        ]

        result = self.chef.generate_report(self.connection)
        expected_result = "Monthly Feedback Report:\nFood Item ID: 1, Average Rating: 4.5, Feedback Count: 10\nFood Item ID: 2, Average Rating: 3.7, Feedback Count: 5\n"
        self.assertEqual(result, expected_result)

    @patch.object(MenuManager, 'view_rolled_out_menu_for_today')
    def test_view_rolled_out_menu_for_today(self, mock_view_rolled_out_menu_for_today):
        mock_view_rolled_out_menu_for_today.return_value = "Rolled Out Menu for Today:\nID: 1, Name: Pizza, Price: 12.99, Meal Type: Lunch"
        result = self.chef.view_rolled_out_menu_for_today()
        self.assertEqual(result, "Rolled Out Menu for Today:\nID: 1, Name: Pizza, Price: 12.99, Meal Type: Lunch")
        mock_view_rolled_out_menu_for_today.assert_called_once_with(123)

    def test_view_feedback_for_questions(self):
        cursor_mock = MagicMock()
        self.connection.cursor.return_value = cursor_mock
        cursor_mock.fetchall.return_value = [
            (1, "How was the meal?", "Great!"),
            (1, "How was the meal?", "Okay."),
            (2, "Any suggestions?", None)
        ]

        result = self.chef.view_feedback_for_questions(self.connection)
        expected_result = "Question ID: 1\nQuestion: How was the meal?\nResponses:\n- Great!\n- Okay.\n\nQuestion ID: 2\nQuestion: Any suggestions?\nResponses:\n- No response yet\n"
        self.assertEqual(result, expected_result)

if __name__ == '__main__':
    unittest.main()

