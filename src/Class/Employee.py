import json
import sys
import os
from datetime import datetime, timedelta
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), 'Class')))
from Recommendation_System import RecommendationEngine
from SQLConnect import create_connection, execute_read_query, execute_query

class Employee:
    def __init__(self, name, employeeid):
        self.name = name
        self.employeeid = employeeid

    def get_role_from_employeeid(self):
        connection = create_connection()
        query = f"SELECT RoleName FROM role WHERE RoleID = (SELECT roleID FROM user WHERE EmployeeID = '{self.employeeid}')"
        get_role = execute_read_query(connection, query)
        if get_role:
            return get_role[0][0]  
        return None

    @staticmethod
    def view_menu(connection, employee_id, availability_only=False):
        try:
            cursor = connection.cursor()
            cursor.execute("SELECT dietary_preference, spice_level, preferred_cuisine, sweet_tooth FROM user WHERE EmployeeID = %s", (employee_id,))
            user = cursor.fetchone()
            if not user:
                return "User not found."

            dietary_preference, spice_level, preferred_cuisine, sweet_tooth = user

            if availability_only:
                cursor.execute("SELECT * FROM fooditem WHERE AvailabilityStatus = 1")
            else:
                cursor.execute("SELECT * FROM fooditem")
            food_items = cursor.fetchall()

            
            def sort_key(item):
                score = 0
                if dietary_preference == item[4]:  # dietary_type
                    score += 10
                if spice_level == item[5]:  # spice_level
                    score += 5
                if preferred_cuisine == item[6]:  # cuisine
                    score += 3
                if sweet_tooth and item[7]:  # is_sweet
                    score += 2
                return score

            sorted_food_items = sorted(food_items, key=sort_key, reverse=True)
            menu = ["Menu:"]
            for item in sorted_food_items:
                menu.append(f"ID: {item[0]}, Name: {item[1]}, Price: {item[2]}, Available: {item[3]}")

            return "\n".join(menu)
        except Exception as e:
            return f"Error fetching menu: {e}"

    @staticmethod
    def select_food_item(connection, employee_id, food_item_id):
        try:
            cursor = connection.cursor()
            cursor.execute("SELECT UserID FROM user WHERE EmployeeID = %s", (employee_id,))
            result = cursor.fetchone()
            if not result:
                return "User not found."
            userid = result[0]
            date = (datetime.today() - timedelta(days=1)).strftime('%Y-%m-%d')

            query = """
            SELECT menu.FoodItemID, fooditem.ItemName, fooditem.Price, menu.MealType
            FROM menu
            JOIN fooditem ON menu.FoodItemID = fooditem.FoodItemID
            WHERE menu.Date = %s
            """
            cursor.execute(query, (date,))
            today_menu = cursor.fetchall()

            if today_menu:
                cursor.execute("SELECT * FROM votetable WHERE UserID = %s AND DATE(VoteDate) = %s AND FoodItemID = %s", 
                               (userid, date, food_item_id))
                user_vote = cursor.fetchone()

                if user_vote:
                    return "You have already selected this food item today."
                else:
                    cursor.execute("INSERT INTO votetable (VoteDate, FoodItemID, UserID) VALUES (%s, %s, %s)",
                                   (date, food_item_id, userid))
                    connection.commit()
                    return "Your food item selection has been recorded."
            else:
                return "No menu items rolled out today."
        except Exception as e:
            return f"Error selecting food item: {e}"

    @staticmethod
    def give_feedback(connection, employee_id, food_item_id, comment, rating):
        try:
            cursor = connection.cursor()
            cursor.execute("SELECT UserID FROM user WHERE EmployeeID = %s", (employee_id,))
            result = cursor.fetchone()
            if not result:
                return "User not found."
            userid = result[0]

            cursor.execute("INSERT INTO feedback (UserID, Comment, Rating, FeedbackDate, FoodItemID) VALUES (%s, %s, %s, CURDATE(), %s)", 
                           (userid, comment, rating, food_item_id))
            connection.commit()
            return "Feedback submitted successfully."
        except Exception as e:
            return f"Error submitting feedback: {e}"
        

    @staticmethod
    def get_pending_question(connection, employee_id):
        try:
            cursor = connection.cursor()
            cursor.execute("SELECT UserID FROM user WHERE EmployeeID = %s", (employee_id,))
            result = cursor.fetchone()
            if not result:
                return None
            user_id = result[0]

            query = """
                SELECT q.question_id, q.question
                FROM question q
                LEFT JOIN survey s ON q.question_id = s.question_id AND s.UserID = %s
                WHERE s.question_id IS NULL
                ORDER BY q.date_sent DESC
                """
            cursor.execute(query, (user_id,))
            results = cursor.fetchall()
            if results:
                questions = "\n".join([f" {question_id}, - '{question_text}'" for question_id, question_text in results])
                return f"Pending Survey Questions:\n{questions}"
            return "No pending survey questions."
        except Exception as e:
            return None
        
    @staticmethod
    def submit_survey_response(connection, employee_id, question_id, response):
        try:
            cursor = connection.cursor()
            cursor.execute("SELECT UserID FROM user WHERE EmployeeID = %s", (employee_id,))
            result = cursor.fetchone()
            if not result:
                return "User not found."
            user_id = result[0]

            cursor.execute("INSERT INTO survey (UserID, Question_id, response) VALUES (%s, %s, %s)",
                           (user_id, question_id, response))
            connection.commit()
            return "Survey response submitted successfully."
        except Exception as e:
            return f"Error submitting survey response: {e}"
        
    def update_employee_profile(connection,dietary_preference,spice_level,preferred_cuisine,sweet_tooth,employee_id):
        try:
            cursor = connection.cursor()
            query = """
                UPDATE user
                SET dietary_preference = %s, spice_level = %s, preferred_cuisine = %s, sweet_tooth = %s
                WHERE EmployeeID = %s
            """
            cursor.execute(query, (dietary_preference, spice_level, preferred_cuisine, sweet_tooth,employee_id))
            connection.commit()
            return "Profile updated successfully."
        except Exception as e:
            print(f"Error updating profile: {e}")
            return f"Error: {e}"

