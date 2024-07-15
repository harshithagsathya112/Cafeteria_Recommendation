import sys
import os
from datetime import datetime, timedelta
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from Models.Menu import MenuManager
from Models.UserLogin import User
from Database.SQLConnect import execute_read_query

class Employee:
    def __init__(self, employee_id):
        self.employee_id = employee_id

    def get_role(self, connection):
        try:
            role_name = self.fetch_role_name(connection)
            return role_name
        except Exception as e:
            return f"Error fetching role: {e}"
    @staticmethod
    def view_menu(connection, employee_id=None, availability_only=False):
        try:
            Menu=MenuManager(connection)
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
            food_items=Menu.sort_menu_items(food_items, dietary_preference, spice_level, preferred_cuisine, sweet_tooth)

            return Menu.format_menu_output(food_items)
        except Exception as e:
            return f"Error fetching menu: {e}"
        
    @staticmethod
    def select_food_item(connection, employee_id, food_item_id):
        try:
            cursor = connection.cursor()
            cursor.execute("SELECT UserID FROM user WHERE EmployeeID = %s", (employee_id,))
            User = cursor.fetchone()
            if not User:
                return "User not found."
            user_id = User[0]
            date = (datetime.today() - timedelta(days=1)).strftime('%Y-%m-%d')

            query = """
            SELECT menu.FoodItemID, fooditem.ItemName, fooditem.Price, menu.MealType
            FROM menu
            JOIN fooditem ON menu.FoodItemID = fooditem.FoodItemID
            WHERE menu.Date = %s
            """
            cursor.execute(query, (date,))
            today_menu = cursor.fetchall()

            if not today_menu:
                return "No menu items rolled out today."

            if Employee.user_already_voted(cursor, user_id, date, food_item_id):
                return "You have already selected this food item today."

            Employee.record_vote(cursor, user_id, date, food_item_id)
            connection.commit()
            return "Your food item selection has been recorded."
    
        except Exception as e:
            return f"Error selecting food item: {e}"
    
        finally:
            cursor.close()
    @staticmethod
    def give_feedback(connection, employee_id,food_item_id, comment, rating):
        try:
            response = Employee.submit_feedback(connection,employee_id, food_item_id, comment, rating)
            return response
        except Exception as e:
            return f"Error submitting feedback: {e}"

    def get_pending_question(self, connection):
        try:
            pending_question_data = self.fetch_pending_questions(connection)
            return pending_question_data
        except Exception as e:
            return f"Error fetching pending questions: {e}"

    def submit_survey_response(self, connection, question_id, response):
        try:
            Response_while_submitting_survey = self.submit_survey(connection, question_id, response)
            return Response_while_submitting_survey 
        except Exception as e:
            return f"Error submitting survey response: {e}"

    def update_profile(self, connection, dietary_preference, spice_level, preferred_cuisine, sweet_tooth):
        try:
            Response_while_Upadating_profile = self.update_employee_profile(connection, dietary_preference, spice_level, preferred_cuisine, sweet_tooth)
            return Response_while_Upadating_profile
        except Exception as e:
            return f"Error updating profile: {e}"

    def fetch_role_name(self, connection):
        employee_role=User.get_role_from_employeeid(self.employee_id)
        return employee_role if employee_role else None
    
    @staticmethod
    def submit_feedback(connection,employee_id,food_item_id, comment, rating):
        cursor = connection.cursor()
        cursor.execute("SELECT UserID FROM user WHERE EmployeeID = %s", (employee_id,))
        User_Details = cursor.fetchone()
        user_id=User_Details[0]
        
        if not user_id:
            return "User not found."

        cursor.execute("""
            INSERT INTO feedback (UserID, Comment, Rating, FeedbackDate, FoodItemID) 
            VALUES (%s, %s, %s, CURDATE(), %s)
        """, (user_id, comment, rating, food_item_id))
        connection.commit()
        return "Feedback submitted successfully."

    def fetch_pending_questions(self, connection):
        cursor = connection.cursor()
        user_id = self.get_user_id(connection)
        if not user_id:
            return "User not found."

        cursor.execute("""
            SELECT q.question_id, q.question
            FROM question q
            LEFT JOIN survey s ON q.question_id = s.question_id AND s.UserID = %s
            WHERE s.question_id IS NULL
            ORDER BY q.date_sent DESC
        """, (user_id,))
        questions = cursor.fetchall()

        if not questions:
            return "No pending survey questions."

        pending_questions = "\n".join([f"{qid}, - '{qtext}'" for qid, qtext in questions])
        return f"Pending Survey Questions:\n{pending_questions}"

    def submit_survey(self, connection, question_id, response):
        cursor = connection.cursor()
        user_id = self.get_user_id(connection)
        if not user_id:
            return "User not found."

        cursor.execute("""
            INSERT INTO survey (UserID, Question_id, response) 
            VALUES (%s, %s, %s)
        """, (user_id, question_id, response))
        connection.commit()
        return "Survey response submitted successfully."

    def update_employee_profile(self, connection, dietary_preference, spice_level, preferred_cuisine, sweet_tooth):
        cursor = connection.cursor()
        cursor.execute("""
            UPDATE user
            SET dietary_preference = %s, spice_level = %s, preferred_cuisine = %s, sweet_tooth = %s
            WHERE EmployeeID = %s
        """, (dietary_preference, spice_level, preferred_cuisine, sweet_tooth, self.employee_id))
        connection.commit()
        return "Profile updated successfully."

    def get_user_id(self, connection):
        cursor = connection.cursor()
        cursor.execute("SELECT UserID FROM user WHERE EmployeeID = %s", (self.employee_id,))
        User_Details = cursor.fetchone()
        return User_Details [0] if User_Details  else None

    def fetch_today_menu(self, connection, date):
        cursor = connection.cursor()
        cursor.execute("""
            SELECT menu.FoodItemID, fooditem.ItemName, fooditem.Price, menu.MealType
            FROM menu
            JOIN fooditem ON menu.FoodItemID = fooditem.FoodItemID
            WHERE menu.Date = %s
        """, (date,))
        return cursor.fetchall()
    
    @staticmethod
    def user_already_voted(cursor, user_id, date, food_item_id):
        cursor.execute("""
        SELECT * 
        FROM votetable 
        WHERE UserID = %s AND DATE(VoteDate) = %s AND FoodItemID = %s
        """, (user_id, date, food_item_id))
        return cursor.fetchone() is not None

    @staticmethod
    def record_vote(cursor, user_id, date, food_item_id):
        cursor.execute("""
            INSERT INTO votetable (VoteDate, FoodItemID, UserID) 
            VALUES (%s, %s, %s)
        """, (date, food_item_id, user_id))
