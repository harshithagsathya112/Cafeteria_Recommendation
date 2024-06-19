import sys
import os
from datetime import datetime, timedelta

# Add the Class directory to the system path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), 'Class')))
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
    def view_menu(connection, availability_only=False):
        try:
            cursor = connection.cursor()
            if availability_only:
                cursor.execute("SELECT * FROM fooditem WHERE AvailabilityStatus = 1")
            else:
                cursor.execute("SELECT * FROM fooditem")
            result = cursor.fetchall()
            menu = ["Menu:"]
            for row in result:
                menu.append(f"ID: {row[0]}, Name: {row[1]}, Price: {row[2]}, Available: {row[3]}")
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
