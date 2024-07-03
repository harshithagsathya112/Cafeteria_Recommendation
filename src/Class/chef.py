from datetime import datetime, timedelta
from Notification import insert_notification_for_all_users


class Chef:
    def __init__(self, user_id, employee_id, name, role_id, password):
        self.user_id = user_id
        self.employee_id = employee_id
        self.name = name
        self.role_id = role_id
        self.password = password

    def roll_out_menu(self, connection, meal_type, food_item_id):
        date = (datetime.today() - timedelta(days=1)).strftime('%Y-%m-%d')

        cursor = connection.cursor()
        cursor.execute("INSERT INTO menu (Date, MealType, FoodItemID) VALUES (%s, %s, %s)", 
                       (date, meal_type, food_item_id))
        cursor.execute("SELECT ItemName FROM fooditem WHERE FoodItemID = %s", (food_item_id,))
        food_name = cursor.fetchone()[0]
        message = f"{food_name} has been add in rolled out menu."
        insert_notification_for_all_users(message)
        connection.commit()
        return "Menu rolled out for the next day."

    def view_feedback(self, connection):
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM feedback")
        result = cursor.fetchall()
        feedback = "Feedback:\n"
        for row in result:
            feedback += f"Feedback ID: {row[0]}, User ID: {row[1]}, Comment: {row[2]}, Rating: {row[3]}, Date: {row[4]}, Food Item ID: {row[5]}\n"
        return feedback

    def generate_report(self, connection):
        cursor = connection.cursor()
        cursor.execute("""
            SELECT FoodItemID, AVG(Rating) as avg_rating, COUNT(*) as feedback_count
            FROM feedback
            GROUP BY FoodItemID
            """)
        result = cursor.fetchall()
        report = "Monthly Feedback Report:\n"
        for row in result:
            report += f"Food Item ID: {row[0]}, Average Rating: {row[1]}, Feedback Count: {row[2]}\n"
        return report

    def send_final_menu(self, connection, meal_type, food_item_id):
        today_date = datetime.today().strftime('%Y-%m-%d')
        previous_date = (datetime.today() - timedelta(days=1)).strftime('%Y-%m-%d')
        day_before_previous_date = (datetime.today() - timedelta(days=2)).strftime('%Y-%m-%d')

        cursor = connection.cursor()

        cursor.execute("SELECT COUNT(*) FROM menu WHERE Date = %s AND FoodItemID = %s", (previous_date, food_item_id))
        count = cursor.fetchone()[0]

        if count == 0:
            cursor.execute("INSERT INTO menu (Date, MealType, FoodItemID, FinalFlag) VALUES (%s, %s, %s, %s)",
                           (previous_date, meal_type, food_item_id, 1))
        else:
            cursor.execute("UPDATE menu SET FinalFlag = %s WHERE Date = %s AND FoodItemID = %s", (1, previous_date, food_item_id))
        
        connection.commit()

        cursor.execute("SELECT FoodItemID FROM menu WHERE Date = %s AND FinalFlag = 1", (previous_date,))
        food_items_with_final_flag = cursor.fetchall()

        for item in food_items_with_final_flag:
            cursor.execute("UPDATE fooditem SET AvailabilityStatus = %s WHERE FoodItemID = %s", 
                           (1, item[0]))
            
            cursor.execute("SELECT ItemName FROM fooditem WHERE FoodItemID = %s", (item[0],))
            food_name = cursor.fetchone()[0]
            message = f"{food_name} is now available."
            insert_notification_for_all_users(message)

        cursor.execute("UPDATE fooditem SET AvailabilityStatus = %s WHERE FoodItemID NOT IN (SELECT FoodItemID FROM menu WHERE Date = %s AND FinalFlag = 1)", 
                       (0, previous_date))

        connection.commit()
        return "Food item is added for today's menu "
    
    def view_feedback_for_questions(self,connection):
        try:
            cursor = connection.cursor()

            # Query to get all questions with their feedback
            query = """
                SELECT q.question_id, q.question, s.response
                FROM question q
                LEFT JOIN survey s ON q.question_id = s.question_id
                ORDER BY q.date_sent DESC, q.question_id ASC
            """
            cursor.execute(query)
            results = cursor.fetchall()

            if not results:
                return "No feedback available."

            formatted_feedback = ""
            current_question_id = None

            for question_id, question_text, response in results:
                if question_id != current_question_id:
                    if current_question_id is not None:
                        formatted_feedback += "\n"
                    formatted_feedback += f"Question ID: {question_id}\nQuestion: {question_text}\nResponses:\n"
                    current_question_id = question_id

                if response:
                    formatted_feedback += f"- {response}\n"
                else:
                    formatted_feedback += "- No response yet\n"

            return formatted_feedback
        except Exception as e:
            return f"Error fetching feedback for questions: {e}"
        
from datetime import datetime, timedelta

def view_rolled_out_menu_for_today(connection, employee_id):
    try:
        cursor = connection.cursor()
        
        # Retrieve user preferences
        cursor.execute("SELECT dietary_preference, spice_level, preferred_cuisine, sweet_tooth FROM user WHERE EmployeeID = %s", (employee_id,))
        user = cursor.fetchone()
        if not user:
            return "User not found."
        
        dietary_preference, spice_level, preferred_cuisine, sweet_tooth = user
        
        # Fetch rolled out menu items
        previous_date = (datetime.today() - timedelta(days=1)).strftime('%Y-%m-%d')
        query = """
        SELECT menu.FoodItemID, fooditem.ItemName, fooditem.Price, menu.MealType, fooditem.DietaryType, fooditem.SpiceLevel, fooditem.Cuisine, fooditem.IsSweet
        FROM menu
        JOIN fooditem ON menu.FoodItemID = fooditem.FoodItemID
        WHERE menu.Date = %s
        """
        cursor.execute(query, (previous_date,))
        result = cursor.fetchall()
        
        if not result:
            return "No menu items rolled out for today."
        
        # Define sorting key function
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

        # Sort menu items based on user preferences
        sorted_menu = sorted(result, key=sort_key, reverse=True)
        
        rolled_out_menu = ["Rolled Out Menu for Today:"]
        for row in sorted_menu:
            rolled_out_menu.append(f"ID: {row[0]}, Name: {row[1]}, Price: {row[2]}, Meal Type: {row[3]}")
        
        return "\n".join(rolled_out_menu)
    
    except Exception as e:
        return f"Error fetching today's rolled-out menu: {e}"
