import os
import sys
import logging

project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(project_root)

from Models.UserLogin import User
from Models.Recommendation_System import RecommendationEngine
from Models.Admin import Admin
from Models.chef import Chef
from Models.Employee import Employee
from Models.Menu import MenuManager
from Utils.Input_Validation import handle_input_request, validate_input, update_profile_input
from Database.SQLConnect import execute_read_query

logging.basicConfig(filename='user_activity.log', level=logging.INFO, format='%(asctime)s - %(message)s')

class User_Service:
    MIN_RATING = 0
    MAX_RATING = 5

    def __init__(self, connection):
        self.connection = connection

    def execute_admin_command(self, choice, args):
        admin = Admin(self.connection)
        match choice:
            case '1':
                return self._add_food_item(admin, args)
            case '2':
                return self._update_food_item(admin, args)
            case '3':
                return self._delete_food_item(admin, args)
            case '4':
                return self._get_food_items(admin)
            case '5':
                return "Logout"
            case _:
                return "Invalid choice!"

    def execute_chef_command(self, choice, employee_id, args):
        chef = Chef(None, employee_id, None, None, None, self.connection)
        engine = RecommendationEngine(self.connection)
        match choice:
            case '1':
                return self._roll_out_menu(chef, args)
            case '2':
                return chef.generate_report(self.connection)
            case '3':
                return chef.fetch_food_items(self.connection)
            case '4':
                return self._send_final_menu(chef, args)
            case '5':
                menu_manager = MenuManager(self.connection)
                return menu_manager.view_rolled_out_menu_for_today(chef.employee_id)
            case '6':
                return engine.recommend_items(top_n=int(args[0]))
            case '7':
                return self._generate_discard_list(engine)
            case 'Remove':
                return self._remove_food_item(args[0])
            case 'Feedback':
                return self._request_detailed_feedback(args[0])
            case '8':
                return chef.view_feedback_for_questions(self.connection)
            case '9':
                return "Logout"
            case _:
                return "Invalid choice!"

    def execute_user_command(self, choice, employee_id, args):
        employee = Employee(employee_id)
        match choice:
            case '1':
                return Employee.view_menu(self.connection, employee_id, availability_only=True)
            case '2':
                return self._select_food_item(employee, args)
            case '3':
                return self._give_feedback(employee, args)
            case '4':
                menu_manager = MenuManager(self.connection)
                return menu_manager.view_rolled_out_menu_for_today(employee_id)
            case '5':
                return employee.get_pending_question(self.connection)
            case '6':
                return employee.submit_survey_response(self.connection, args[0], args[1])
            case '7':
                return self._update_employee_profile(employee, args)
            case '8':
                return "Logout"
            case _:
                return "Invalid choice!"

    def _add_food_item(self, admin, args):
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

    def _update_food_item(self, admin, args):
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

    def _delete_food_item(self, admin, args):
        foodid = args[0]
        try:
            foodid = int(foodid)
            if not self.food_item_exists(foodid):
                raise ValueError(f"Food ID {foodid} does not exist.")
            admin.delete_food_item(foodid)
            return "Food item deleted successfully."
        except Exception as e:
            return f"Error deleting food item: {e}"

    def _get_food_items(self, admin):
        try:
            return admin.get_food_items()
        except Exception as e:
            return f"Error fetching food items: {e}"

    def _roll_out_menu(self, chef, args):
        meal_type, food_item_id = args
        try:
            food_item_id = int(food_item_id)
            if not self.food_item_exists(food_item_id):
                raise ValueError(f"Food item ID {food_item_id} does not exist.")
            return chef.roll_out_menu(meal_type, food_item_id)
        except Exception as e:
            return f"Error rolling out menu: {e}"

    def _send_final_menu(self, chef, args):
        meal_type, food_item_id = args
        try:
            food_item_id = int(food_item_id)
            if not self.food_item_exists(food_item_id):
                raise ValueError(f"Food item ID {food_item_id} does not exist.")
            return chef.send_final_menu(meal_type, food_item_id)
        except Exception as e:
            return f"Error sending final menu: {e}"

    def _generate_discard_list(self, engine):
        discard_list = engine.generate_discard_list()
        output = "Discard Menu Item List:\n"
        for item in discard_list:
            output += f"- ID: {item[0]}, Name: {item[1]} (Rating: {item[2]:.2f}, Sentiment: {item[3]})\n"

        output += "\nConsole Options:\n"
        output += "Enter --Remove-- to Remove the Food Item from Menu List\n"
        output += "Enter --Feedback-- to send Feedback request to users\n"
        return output

    def _remove_food_item(self, food_item_id):
        try:
            admin = Admin(self.connection)
            food_item_id_to_remove = int(food_item_id)
            admin.delete_food_item(food_item_id_to_remove)
            return "Food Item is deleted successfully"
        except Exception as e:
            return f"Error removing food item: {e}"

    def _request_detailed_feedback(self, food_item_id):
        try:
            engine = RecommendationEngine(self.connection)
            food_item_id_to_get_feedback = int(food_item_id)
            engine.request_detailed_feedback(food_item_id_to_get_feedback)
            return "Feedback sent successfully"
        except Exception as e:
            return f"Error requesting feedback: {e}"

    def _select_food_item(self, employee, args):
        food_item_id = args[0]
        try:
            food_item_id = int(food_item_id)
            if not self.food_item_exists(food_item_id):
                raise ValueError(f"Food item ID {food_item_id} does not exist.")
            return Employee.select_food_item(self.connection, employee.employee_id, food_item_id)
        except Exception as e:
            return f"Error selecting food item: {e}"

    def _give_feedback(self, employee, args):
        food_item_id, comment, rating = args
        try:
            food_item_id = int(food_item_id)
            if not self.food_item_exists(food_item_id):
                raise ValueError(f"Food item ID {food_item_id} does not exist.")
            if not isinstance(comment, str):
                raise ValueError("Comment must be a string.")
            rating = float(rating)
            if not self.is_valid_rating(rating):
                raise ValueError("Rating must be a number between 0 and 5.")
            return employee.give_feedback(self.connection, employee.employee_id, food_item_id, comment, rating)
        except Exception as e:
            return f"Error giving feedback: {e}"

    def is_valid_rating(self, rating):
        return self.MIN_RATING <= rating <= self.MAX_RATING

    def _update_employee_profile(self, employee, args):
        dietary_preference, spice_level, preferred_cuisine, sweet_tooth = args
        try:
            return employee.update_employee_profile(self.connection, dietary_preference, spice_level, preferred_cuisine, sweet_tooth)
        except Exception as e:
            return f"Error updating employee profile: {e}"

    def view_menu(self, availability_only=False):
        return Employee.view_menu(self.connection, 1001, availability_only)

    def food_item_exists(self, food_item_id):
        try:
            cursor = self.connection.cursor()
            cursor.execute("SELECT COUNT(*) FROM fooditem WHERE FoodItemID = %s", (food_item_id,))
            fooditem_count = cursor.fetchone()[0]
            return fooditem_count > 0
        except Exception as e:
            print(f"Error checking food item existence: {e}")
            return False
