import os
import sys
import random
from datetime import datetime, timedelta

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from SQLConnect import create_connection, execute_read_query

class RecommendationEngine:
    def __init__(self, connection, sentiment_words_file):
        self.connection = connection
        base_dir = os.path.dirname(os.path.dirname(__file__))  # This navigates up to the `src` directory
        sentiment_file_path = os.path.join(base_dir, 'Data', 'sentiment_words.txt')  # Path to the sentiment_words.txt
        self.positive_words, self.negative_words = self.load_sentiment_words(sentiment_file_path)


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

    def simple_sentiment_analysis(self, comment):
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

        total_rating = 0
        total_feedback = 0
        sentiment_score = 0
        food_name = ""

        for comment, rating, name in feedbacks:
            total_rating += rating
            total_feedback += 1
            sentiment_score += self.simple_sentiment_analysis(comment)
            food_name = name  # All rows will have the same name for this food item

        average_rating = total_rating / total_feedback if total_feedback else 0
        average_sentiment_score = sentiment_score / total_feedback if total_feedback else 0
        sentiment_category = self.categorize_sentiment(average_sentiment_score)

        return food_name, average_rating, sentiment_category

    '''@staticmethod
    def generate_dummy_data(connection):
        cursor = connection.cursor()

        # Generate dummy users
        users = [
            ("1001", "John Doe", 3, "password1"),
            ("1002", "Jane Smith", 3, "password2"),
            ("1003", "Emily Davis", 3, "password3")
        ]

        for employee_id, name, role_id, password in users:
            cursor.execute("INSERT INTO user (EmployeeID, Name, RoleID, Password) VALUES (%s, %s, %s, %s)",
                           (employee_id, name, role_id, password))
        connection.commit()

        # Generate dummy food items
        food_items = [
            (1, "Pasta", 7.99, 1),
            (2, "Pizza", 9.99, 1),
            (3, "Burger", 5.99, 1)
        ]

        for food_item_id, item_name, price, availability_status in food_items:
            cursor.execute("INSERT INTO fooditem (FoodItemID, ItemName, Price, AvailabilityStatus, LookupID) VALUES (%s, %s, %s, %s, %s)",
                           (food_item_id, item_name, price, availability_status, food_item_id))
        connection.commit()

        # Generate dummy menu items
        menu_items = [
            (datetime.today().strftime('%Y-%m-%d'), "breakfast", 1, 0),
            (datetime.today().strftime('%Y-%m-%d'), "lunch", 2, 0),
            (datetime.today().strftime('%Y-%m-%d'), "dinner", 3, 0)
        ]

        for date, meal_type, food_item_id, final_flag in menu_items:
            cursor.execute("INSERT INTO menu (Date, MealType, FoodItemID, FinalFlag) VALUES (%s, %s, %s, %s)",
                           (date, meal_type, food_item_id, final_flag))
        connection.commit()

        # Generate dummy feedback
        feedback_comments = [
            ("Great taste!", 5),
            ("Too salty.", 2),
            ("Loved it!", 4),
            ("Not my favorite.", 3),
            ("Perfectly cooked!", 5)
        ]

        for _ in range(10):
            user_id = random.randint(1, len(users))
            food_item_id = random.randint(1, len(food_items))
            comment, rating = random.choice(feedback_comments)
            feedback_date = (datetime.today() - timedelta(days=random.randint(1, 30))).strftime('%Y-%m-%d')

            cursor.execute("INSERT INTO feedback (UserID, FoodItemID, Comment, Rating, FeedbackDate) VALUES (%s, %s, %s, %s, %s)",
                           (user_id, food_item_id, comment, rating, feedback_date))
        connection.commit()

        cursor.close()'''

# Example usage:
if __name__ == "__main__":
    connection = create_connection()

    if connection:
        sentiment_words_path = os.path.join(os.path.dirname(__file__), 'sentiment_words.txt')
        engine = RecommendationEngine(connection, sentiment_words_path)

        # Analyze feedback for a specific food item
        food_item_id = 21
        food_name,average_rating, sentiment_category = engine.analyze_feedback(food_item_id)

        print(f"Average Rating for {food_name}: {average_rating}")
        print(f"Sentiment for {food_name}: {sentiment_category}")
        
        connection.close()
