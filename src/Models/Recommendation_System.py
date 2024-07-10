import os
import sys
from datetime import datetime, timedelta
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(project_root)
from Models.Admin import Admin
from Models.Notification import Notification
from Models.Support_functions import get_food_name
from Database.SQLConnect import execute_read_query

class RecommendationEngine:

    def __init__(self, connection):
        self.connection = connection
        base_dir = os.path.dirname(os.path.dirname(__file__))
        sentiment_file_path = os.path.join(base_dir, 'Data', 'sentiment_words.txt')
        self.positive_words, self.negative_words = self.load_sentiment_words(sentiment_file_path)
        self.admin = Admin(connection)
        self.Notification=Notification()

    def load_sentiment_words(self, sentiment_words_file):
        positive_words = []
        negative_words = []
        with open(sentiment_words_file, 'r') as sentiment_data_file:
            sentiment_file_lines = sentiment_data_file.readlines()
            current_list = None
            for line in sentiment_file_lines:
                line = line.strip()
                if line == "positive:":
                    current_list = positive_words
                elif line == "negative:":
                    current_list = negative_words
                elif line and current_list is not None:
                    words = line.split(", ")
                    current_list.extend(words)
        return positive_words, negative_words

    def give_sentiment_score(self, comment):
        comment_words = comment.lower().split()
        sentiment_score = 0
        for word in comment_words:
            if word in self.positive_words:
                sentiment_score += 1
            elif word in self.negative_words:
                sentiment_score -= 1
        return sentiment_score

    def categorize_sentiment(self, sentiment_score):
        if sentiment_score > 0:
            return "Positive"
        elif sentiment_score < 0:
            return "Negative"
        else:
            return "Neutral"

    def analyze_feedback(self, food_item_id):
        query_to_fetch_feedback_of_fooditem = f"""
        SELECT f.Comment, f.Rating, fi.ItemName
        FROM feedback f
        JOIN fooditem fi ON f.FoodItemID = fi.FoodItemID
        WHERE f.FoodItemID = {food_item_id}
        """
        feedbacks = execute_read_query(self.connection, query_to_fetch_feedback_of_fooditem )

        if not feedbacks:
            query_to_fetch_foodItem_name = f"SELECT ItemName FROM fooditem WHERE FoodItemID = {food_item_id}"
            FoodItem_details = execute_read_query(self.connection, query_to_fetch_foodItem_name)
            food_name = FoodItem_details[0][0] if FoodItem_details else "Unknown Food Item"
            return food_name, 0, "Neutral"

        total_rating = 0
        total_feedback = 0
        sentiment_score = 0
        food_name = ""

        for comment, rating, name in feedbacks:
            total_rating += rating
            total_feedback += 1
            sentiment_score += self.give_sentiment_score(comment)
            food_name = name

        average_rating = total_rating / total_feedback if total_feedback else 0
        average_sentiment_score = sentiment_score / total_feedback if total_feedback else 0
        sentiment_category = self.categorize_sentiment(average_sentiment_score)

        return food_name, average_rating, sentiment_category

    def count_votes(self, food_item_id):
        previous_date = (datetime.today() - timedelta(days=1)).strftime('%Y-%m-%d')
        query_to_fetch_votes_fooditems = f"""
        SELECT COUNT(*) FROM votetable
        WHERE FoodItemID = {food_item_id} AND DATE(VoteDate) = '{previous_date}'
        """
        total_votes = execute_read_query(self.connection, query_to_fetch_votes_fooditems)
        return total_votes[0][0] if total_votes else 0

    def recommend_items(self, top_n=3):
        Query_fetch_fooditems = "SELECT FoodItemID FROM fooditem"
        food_items = execute_read_query(self.connection, Query_fetch_fooditems)

        recommendations = []

        for (food_item_id,) in food_items:
            food_name, average_rating, sentiment_category = self.analyze_feedback(food_item_id)
            vote_count = self.count_votes(food_item_id)
            sentiment_score = {"Positive": 1, "Neutral": 0, "Negative": -1}[sentiment_category]
            combined_score = average_rating + sentiment_score + 2 * vote_count

            recommendations.append((food_item_id, food_name, combined_score))

        recommendations.sort(key=lambda x: x[2], reverse=True)

        top_recommendations = recommendations[:top_n]
        result = "\n".join([f"ID: {food_id}, Name: {food_name}, Score: {score:.2f}" for food_id, food_name, score in top_recommendations])
        return result

    def generate_discard_list(self):
        Query_fetch_fooditems = "SELECT FoodItemID FROM fooditem"
        food_items = execute_read_query(self.connection, Query_fetch_fooditems)

        discard_list = []

        for (food_item_id,) in food_items:
            food_name, average_rating, sentiment_category = self.analyze_feedback(food_item_id)
            if average_rating < 2 or sentiment_category == "Negative":
                discard_list.append((food_item_id, food_name, average_rating, sentiment_category))

        return discard_list

    def request_detailed_feedback(self, food_item_id):
        food_name=get_food_name(self.connection,food_item_id)
        questions = [
            f"What didn’t you like about {food_name}?",
            f"How would you like {food_name} to taste?",
            "Share your mom’s recipe."
        ]
        for question in questions:
            question_id = self.insert_question(question)
            self.Notification.send_notification_to_all_users(self.connection,question)

        questions.append(f"\nWe are trying to improve your experience with {food_name}. Please provide your feedback and help us.")
        self.Notification.send_notification_to_all_users(self.connection,f"\nWe are trying to improve your experience with {food_name}. Please provide your feedback and help us.")
        return questions
    
    def insert_question(self, question_text):
        cursor = self.connection.cursor()
        cursor.execute("INSERT INTO question (Question, date_sent) VALUES (%s, CURDATE())", (question_text,))
        self.connection.commit()
        return cursor.lastrowid

