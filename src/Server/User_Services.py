import os
import sys
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(project_root)
from Models.UserLogin import User
from Models.Recommendation_System import RecommendationEngine
from Models.Admin import Admin
from Models.chef import Chef
from Models.Employee import Employee
from Models.Menu import MenuManager
import logging
logging.basicConfig(filename='user_activity.log', level=logging.INFO, format='%(asctime)s - %(message)s')

class User_Service:
    def __init__(self, connection):
        self.connection = connection

    def execute_admin_command(self, choice, args):
        admin = Admin(self.connection)
        match choice:
            case '1':
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
            case '2':
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
            case '3':
                foodid = args[0]
                try:
                    foodid = int(foodid)
                    if not self.food_item_exists(foodid):
                        raise ValueError(f"Food ID {foodid} does not exist.")
                    admin.delete_food_item(foodid)
                    return "Food item deleted successfully."
                except Exception as e:
                    return f"Error deleting food item: {e}"
            case '4':
                try:
                    return admin.get_food_items()
                except Exception as e:
                    return f"Error fetching food items: {e}"
            case '5':
                return "Logout"
            case _:
                return "Invalid choice!"

    def execute_chef_command(self, choice, employee_id, args):
        chef = Chef(None, employee_id, None, None, None,self.connection)
        engine = RecommendationEngine(self.connection)
        match choice:
            case '1':
                meal_type, food_item_id = args
                try:
                    food_item_id = int(food_item_id)
                    if not self.food_item_exists(food_item_id):
                        raise ValueError(f"Food item ID {food_item_id} does not exist.")
                    return chef.roll_out_menu(meal_type, food_item_id)
                except Exception as e:
                    return f"Error rolling out menu: {e}"
            case '2':
                return chef.view_feedback(self.connection)
            case '3':
                return chef.generate_report(self.connection)
            case '4':
                return chef.fetch_food_items(self.connection)
            case '5':
                meal_type, food_item_id = args
                try:
                    food_item_id = int(food_item_id)
                    if not self.food_item_exists(food_item_id):
                        raise ValueError(f"Food item ID {food_item_id} does not exist.")
                    return chef.send_final_menu(meal_type, food_item_id)
                except Exception as e:
                    return f"Error sending final menu: {e}"
            case '6':
                Menu= MenuManager(self.connection)
                return Menu.view_rolled_out_menu_for_today(chef.employee_id)
            case '7':
                no_items_recommended = int(args[0])
                return engine.recommend_items(top_n=no_items_recommended)
            case '8':
                discard_list = engine.generate_discard_list()
                output = "Discard Menu Item List:\n"
                for item in discard_list:
                    output += f"- ID: {item[0]}, Name: {item[1]} (Rating: {item[2]:.2f}, Sentiment: {item[3]})\n"

                output += "\nConsole Options:\n"
                output += "Enter --Remove-- to Remove the Food Item from Menu List\n"
                output += "Enter --Feedback-- to send Feedback request to users\n"
                return output
            case 'Remove':
                admin = Admin(self.connection)
                food_item_id_to_remove = int(args[0])
                admin.delete_food_item(food_item_id_to_remove)
                return "Food Item is deleted successfully"
            case 'Feedback':
                food_item_id_to_get_feedback = int(args[0])
                engine.request_detailed_feedback(food_item_id_to_get_feedback)
                return "Feedback sent successfully"
            case '9':
                return chef.view_feedback_for_questions(self.connection)
            case '10':
                return "Logout"
            case _:
                return "Invalid choice!"

    def execute_user_command(self, choice, employee_id, args):
        employee=Employee(employee_id)
        match choice:
            case '1':
                return Employee.view_menu(self.connection, employee_id, availability_only=True)
            case '2':
                food_item_id = args[0]
                try:
                    food_item_id = int(food_item_id)
                    if not self.food_item_exists(food_item_id):
                        raise ValueError(f"Food item ID {food_item_id} does not exist.")
                    return Employee.select_food_item(self.connection, employee_id, food_item_id)
                except Exception as e:
                    return f"Error selecting food item: {e}"
            case '3':
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
                    return employee.give_feedback(self.connection, employee_id, food_item_id, comment, rating)
                except Exception as e:
                    return f"Error giving feedback: {e}"
            case '4':
                Menu=MenuManager(self.connection)
                return Menu.view_rolled_out_menu_for_today(employee_id)
            case '5':
                return employee.get_pending_question(self.connection)
            case '6':
                question_id, response = args
                return employee.submit_survey_response(self.connection, question_id, response)
            case '7':
                dietary_preference, spice_level, preferred_cuisine, sweet_tooth = args
                return employee.update_employee_profile(self.connection, dietary_preference, spice_level, preferred_cuisine, sweet_tooth)
            case '8':
                return "Logout"
            case _:
                return "Invalid choice!"

    def view_menu(self, availability_only=False):
        return Employee.view_menu(self.connection,1001,availability_only)

    def food_item_exists(self, food_item_id):
        try:
            cursor = self.connection.cursor()
            cursor.execute("SELECT COUNT(*) FROM fooditem WHERE FoodItemID = %s", (food_item_id,))
            result = cursor.fetchone()
            return result[0] > 0
        except Exception as e:
            print(f"Error checking food item existence: {e}")
            return False
