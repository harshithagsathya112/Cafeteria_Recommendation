from datetime import datetime, timedelta
import sys,os
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(project_root)
from Models.Menu import MenuManager

class Chef:
    def __init__(self, user_id, employee_id, name, role_id, password, connection):
        self.user_id = user_id
        self.employee_id = employee_id
        self.name = name
        self.role_id = role_id
        self.password = password
        self.connection=connection

    def fetch_food_items(self, connection):
        try:
            cursor = connection.cursor()
            cursor.execute("SELECT * FROM fooditem")
            food_items = cursor.fetchall()
            menu = ["Menu:"]
            for item in food_items:
                menu.append(f"ID: {item[0]}, Name: {item[1]}, Price: {item[2]}, Available: {item[3]}")
            return "\n".join(menu)
        except Exception as e:
            return f"Error fetching menu: {e}"

    def roll_out_menu(self,meal_type, food_item_id):
        menu_manager = MenuManager(self.connection) 
        return menu_manager.roll_out_menu(meal_type, food_item_id)

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

    def send_final_menu(self, meal_type, food_item_id):
        menu_manager = MenuManager(self.connection) 
        return menu_manager.update_menu_and_availability_status(meal_type, food_item_id)

    def view_feedback_for_questions(self, connection):
        try:
            cursor = connection.cursor()

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

    def view_rolled_out_menu_for_today(self):
        menu_manager = MenuManager(self.connection) 
        return menu_manager.view_rolled_out_menu_for_today(self.employee_id)
