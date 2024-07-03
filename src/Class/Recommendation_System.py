import os
import sys
from datetime import datetime, timedelta
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(project_root)
from Class.Admin import Admin
from Class.Notification import insert_notification_for_all_users
from Class.Support_functions import get_food_name
from SQLConnect import create_connection, execute_read_query

class RecommendationEngine:
    def __init__(self, connection):
        self.connection = connection
        base_dir = os.path.dirname(os.path.dirname(__file__))
        sentiment_file_path = os.path.join(base_dir, 'Data', 'sentiment_words.txt')
        self.positive_words, self.negative_words = self.load_sentiment_words(sentiment_file_path)
        self.admin = Admin()

    def load_sentiment_words(self, sentiment_words_file):
        positive_words = []
        negative_words = []
        with open(sentiment_words_file, 'r') as file:
            lines = file.readlines()
            current_list = None
            for line in lines:
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
        query = f"""
        SELECT f.Comment, f.Rating, fi.ItemName
        FROM feedback f
        JOIN fooditem fi ON f.FoodItemID = fi.FoodItemID
        WHERE f.FoodItemID = {food_item_id}
        """
        feedbacks = execute_read_query(self.connection, query)

        if not feedbacks:
            query = f"SELECT ItemName FROM fooditem WHERE FoodItemID = {food_item_id}"
            result = execute_read_query(self.connection, query)
            food_name = result[0][0] if result else "Unknown Food Item"
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
        query = f"""
        SELECT COUNT(*) FROM votetable
        WHERE FoodItemID = {food_item_id} AND DATE(VoteDate) = '{previous_date}'
        """
        total_votes = execute_read_query(self.connection, query)
        return total_votes[0][0] if total_votes else 0

    def recommend_items(self, top_n=3):
        query = "SELECT FoodItemID FROM fooditem"
        food_items = execute_read_query(self.connection, query)

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
        query = "SELECT FoodItemID FROM fooditem"
        food_items = execute_read_query(self.connection, query)

        discard_list = []

        for (food_item_id,) in food_items:
            food_name, average_rating, sentiment_category = self.analyze_feedback(food_item_id)
            if average_rating < 2 or sentiment_category == "Negative":
                discard_list.append((food_item_id, food_name, average_rating, sentiment_category))

        return discard_list

    def console_options(self):
        discard_list = self.generate_discard_list()
        print("Discard Menu Item List:")
        for item in discard_list:
            print(f"- ID: {item[0]}, Name: {item[1]} (Rating: {item[2]:.2f}, Sentiment: {item[3]})")

        print("\nConsole Options:")
        print("1) Remove the Food Item from Menu List")
        print("2) Get Detailed Feedback")

        choice = input("\nEnter your choice (1 or 2): ")
        if choice == '1':
            food_item_to_remove = input("Enter the food item id to remove from menu: ")
            self.admin.delete_food_item(food_item_to_remove)
        elif choice == '2':
            food_item_to_improve = input("Enter the food item name to get detailed feedback: ")
            self.request_detailed_feedback(food_item_to_improve)
        else:
            print("Invalid choice.")

    def request_detailed_feedback(self, food_item_id):
        food_name=get_food_name(food_item_id)
        questions = [
            f"What didn’t you like about {food_name}?",
            f"How would you like {food_name} to taste?",
            "Share your mom’s recipe."
        ]
        for question in questions:
            question_id = self.insert_question(question)
            insert_notification_for_all_users(question)

        questions.append(f"\nWe are trying to improve your experience with {food_name}. Please provide your feedback and help us.")
        insert_notification_for_all_users(f"\nWe are trying to improve your experience with {food_name}. Please provide your feedback and help us.")
        return questions
    
    def insert_question(self, question_text):
        cursor = self.connection.cursor()
        cursor.execute("INSERT INTO question (Question, date_sent) VALUES (%s, CURDATE())", (question_text,))
        self.connection.commit()
        return cursor.lastrowid

if __name__ == "__main__":
    connection = create_connection()
    engine = RecommendationEngine(connection)
    top_recommendations = engine.recommend_items(top_n=3)
    print(top_recommendations)
    engine.console_options()
