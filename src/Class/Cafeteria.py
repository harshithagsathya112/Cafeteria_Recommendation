import os
import sys
from datetime import datetime, timedelta
from chef import view_rolled_out_menu_for_today
from UserLogin import User
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), 'Class')))
from Logger import log_activity
from SQLConnect import create_connection
from Recommendation_System import RecommendationEngine
from Admin import Admin
from chef import Chef
from Employee import Employee
import logging
logging.basicConfig(filename='user_activity.log', level=logging.INFO, format='%(asctime)s - %(message)s')


class Cafeteria:
    def __init__(self, connection):
        self.connection = connection

    def execute_admin_command(self, choice, args):
        admin = Admin()
        if choice == '1':
            foodname, foodprice = args
            try:
                if not isinstance(foodname, str) or foodname.isdigit():
                    raise ValueError("Food name must be a non-numeric string.")
                foodprice = float(foodprice)
                if foodprice <= 0:
                    raise ValueError("Food price must be a positive number.")
                admin.add_food_item(foodname, foodprice)
                return "Food item added successfully."
            except Exception as e:
                return f"Error adding food item: {e}"
        elif choice == '2':
            foodid, foodname, foodprice = args
            try:
                foodid = int(foodid)
                if not self.food_item_exists(foodid):
                    raise ValueError(f"Food ID {foodid} does not exist.")
                if not isinstance(foodname, str) or foodname.isdigit():
                    raise ValueError("Food name must be a non-numeric string.")
                foodprice = float(foodprice)
                if foodprice <= 0:
                    raise ValueError("Food price must be a positive number.")
                admin.update_food_item(foodid, foodname, foodprice)
                return "Food item updated successfully."
            except Exception as e:
                return f"Error updating food item: {e}"
        elif choice == '3':
            foodid = args[0]
            try:
                foodid = int(foodid)
                if not self.food_item_exists(foodid):
                    raise ValueError(f"Food ID {foodid} does not exist.")
                admin.delete_food_item(foodid)
                return "Food item deleted successfully."
            except Exception as e:
                return f"Error deleting food item: {e}"
        elif choice == '4':
            try:
                return admin.get_food_items()
            except Exception as e:
                return f"Error fetching food items: {e}"
        elif choice == '5':
            return "Logout"
        else:
            return "Invalid choice!"

    def execute_chef_command(self, choice, args):
        chef = Chef(None, None, None, None, None)
        engine = RecommendationEngine(self.connection)
        if choice == '1':
            meal_type, food_item_id = args
            try:
                food_item_id = int(food_item_id)
                if not self.food_item_exists(food_item_id):
                    raise ValueError(f"Food item ID {food_item_id} does not exist.")
                return chef.roll_out_menu(self.connection, meal_type, food_item_id)
            except Exception as e:
                return f"Error rolling out menu: {e}"
        elif choice == '2':
            return chef.view_feedback(self.connection)
        elif choice == '3':
            return chef.generate_report(self.connection)
        elif choice == '4':
            return self.view_menu()
        elif choice == '5':
            meal_type, food_item_id = args
            try:
                food_item_id = int(food_item_id)
                if not self.food_item_exists(food_item_id):
                    raise ValueError(f"Food item ID {food_item_id} does not exist.")
                return chef.send_final_menu(self.connection, meal_type, food_item_id)
            except Exception as e:
                return f"Error sending final menu: {e}"
        elif choice == '6':
            return view_rolled_out_menu_for_today(self.connection)
        elif choice == '7':
            no_items_recommended = int(args[0])
            engine = RecommendationEngine(self.connection)
            return engine.recommend_items(top_n=no_items_recommended)
        elif choice == '8':
            discard_list = engine.generate_discard_list()
            output = "Discard Menu Item List:\n"
            for item in discard_list:
                output += f"- ID: {item[0]}, Name: {item[1]} (Rating: {item[2]:.2f}, Sentiment: {item[3]})\n"

            output += "\nConsole Options:\n"
            output += "Enter --Remove-- to Remove the Food Item from Menu List\n"
            output += "Enter --Feedback-- to send Feedback request to users\n"
            return output
        
        elif choice=='Remove':
            admin=Admin()
            food_item_id_to_remove = int(args[0])
            admin.delete_food_item(food_item_id_to_remove)
            return "Food Item is deleted successfully"
        
        elif choice=='Feedback':
            food_item_id_to_get_feedback = int(args[0])
            engine.request_detailed_feedback(food_item_id_to_get_feedback)
            return "feedback sent successfully"
        elif choice == '9':
            return chef.view_feedback_for_questions(self.connection)
        elif choice == '10':
            return "Logout"
        else:
            return "Invalid choice!"

    def execute_user_command(self, choice, employee_id, args):
        if choice == '1':
            return Employee.view_menu(self.connection,employee_id, availability_only=True)
        elif choice == '2':
            food_item_id = args[0]
            try:
                food_item_id = int(food_item_id)
                if not self.food_item_exists(food_item_id):
                    raise ValueError(f"Food item ID {food_item_id} does not exist.")
                return Employee.select_food_item(self.connection, employee_id, food_item_id)
            except Exception as e:
                return f"Error selecting food item: {e}"
        elif choice == '3':
            food_item_id, comment, rating = args
            try:
                food_item_id = int(food_item_id)
                if not self.food_item_exists(food_item_id):
                    raise ValueError(f"Food item ID {food_item_id} does not exist.")
                if not isinstance(comment, str):
                    raise ValueError("Comment must be a string.")
                rating = float(rating)
                if rating < 0 or rating > 5:
                    raise ValueError("Rating must be a number between 0 and 5.")
                return Employee.give_feedback(self.connection, employee_id, food_item_id, comment, rating)
            except Exception as e:
                return f"Error giving feedback: {e}"
        elif choice == '4':
            return view_rolled_out_menu_for_today(self.connection,employee_id)
        elif choice == '5':
            return Employee.get_pending_question(self.connection,employee_id)
        elif choice == '6':
            question_id, response = args
            return Employee.submit_survey_response(self.connection, employee_id, question_id, response)
        elif choice == '7':
            dietary_preference,spice_level,preferred_cuisine,sweet_tooth = args
            return Employee.update_employee_profile(self.connection, dietary_preference,spice_level,preferred_cuisine,sweet_tooth ,employee_id )
        elif choice == '8':
            return "Logout"
        else:
            return "Invalid choice!"

    def view_menu(self,employee_id, availability_only=False):
        return Employee.view_menu(self.connection, availability_only)

    def food_item_exists(self, food_item_id):
        try:
            connection = create_connection()
            cursor=connection.cursor()
            cursor.execute("SELECT COUNT(*) FROM fooditem WHERE FoodItemID = %s", (food_item_id,))
            result = cursor.fetchone()
            return result[0] > 0
        except Exception as e:
            print(f"Error checking food item existence: {e}")
            return False

def App_run():
    connection = create_connection()
    menu_system = Cafeteria(connection)
    role, employee_id = User.verify_employee()
    menu_system.display_menu(role, employee_id)

if __name__ == "__main__":
    App_run()
