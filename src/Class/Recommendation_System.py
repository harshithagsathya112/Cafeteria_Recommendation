import os
import sys
from datetime import datetime, timedelta

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from SQLConnect import create_connection, execute_read_query

class RecommendationEngine:
    def __init__(self, connection):
        self.connection = connection
        base_dir = os.path.dirname(os.path.dirname(__file__)) 
        sentiment_file_path = os.path.join(base_dir, 'Data', 'sentiment_words.txt') 
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

    def Give_Sentiment_Score(self, comment):
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
            sentiment_score += self.Give_Sentiment_Score(comment)
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
            combined_score = average_rating + sentiment_score + 2*(vote_count) 

            recommendations.append((food_item_id, food_name, combined_score))

        recommendations.sort(key=lambda x: x[2], reverse=True)
        
        top_recommendations = recommendations[:top_n]
        result = "\n".join([f"ID: {food_id}, Name: {food_name}, Score: {score:.2f}" for food_id, food_name, score in top_recommendations])
        return result


if __name__ == "__main__":
    connection = create_connection()
    engine = RecommendationEngine(connection)
    top_recommendations = engine.recommend_items(top_n=3)
    print(top_recommendations)
