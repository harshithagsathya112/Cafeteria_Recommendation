import os
import sys
import unittest
from unittest.mock import Mock, patch
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from Models.Recommendation_System import RecommendationEngine

class TestRecommendationEngine(unittest.TestCase):

    @patch('Models.Recommendation_System.execute_read_query')
    def test_analyze_feedback(self, mock_execute_read_query):
        mock_connection = Mock()
        mock_execute_read_query.return_value = [('Great food!', 4, 'Burger')]

        engine = RecommendationEngine(mock_connection)
        food_name, average_rating, sentiment_category = engine.analyze_feedback(1)

        self.assertEqual(food_name, 'Burger')
        self.assertEqual(average_rating, 4)
        self.assertEqual(sentiment_category, 'Positive')

        mock_execute_read_query.assert_called_once()

    @patch('Models.Recommendation_System.execute_read_query')
    def test_count_votes(self, mock_execute_read_query):
        mock_connection = Mock()
        mock_execute_read_query.return_value = [(5,)]

        engine = RecommendationEngine(mock_connection)
        total_votes = engine.count_votes(1)

        self.assertEqual(total_votes, 5)

        mock_execute_read_query.assert_called_once()

    @patch('Models.Recommendation_System.execute_read_query')
    def test_recommend_items(self, mock_execute_read_query):
        mock_connection = Mock()
        mock_execute_read_query.return_value = [(1,), (2,), (3,)]

        engine = RecommendationEngine(mock_connection)
        recommendations = engine.recommend_items(top_n=3)

        self.assertIn("ID: ", recommendations)
        self.assertIn("Name: ", recommendations)
        self.assertIn("Score: ", recommendations)

        mock_execute_read_query.assert_called_once()

    @patch('Models.Recommendation_System.execute_read_query')
    def test_generate_discard_list(self, mock_execute_read_query):
        mock_connection = Mock()
        mock_execute_read_query.return_value = [(1,), (2,), (3,)]

        engine = RecommendationEngine(mock_connection)
        discard_list = engine.generate_discard_list()

        for (food_item_id,) in discard_list:
            self.assertIsInstance(food_item_id, int)

        mock_execute_read_query.assert_called_once()

    @patch('Models.Recommendation_System.execute_read_query')
    @patch('Models.Recommendation_System.RecommendationEngine.insert_question')
    @patch('Models.Recommendation_System.Notification')
    @patch('Models.Recommendation_System.get_food_name')
    def test_request_detailed_feedback(self, mock_get_food_name, mock_notification, mock_insert_question, mock_execute_read_query):
        mock_connection = Mock()
        mock_get_food_name.return_value = ('Burger',)

        mock_execute_read_query.return_value = [('Great food!', 4, 'Burger')]

        engine = RecommendationEngine(mock_connection)
        questions = engine.request_detailed_feedback(1)

        self.assertEqual(len(questions), 4)

        mock_insert_question.assert_called()
        mock_notification.send_notification_to_all_users.assert_called()

        mock_execute_read_query.assert_called_once()

if __name__ == '__main__':
    unittest.main()
