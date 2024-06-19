import os
import sys
from datetime import datetime, timedelta
from chef import view_rolled_out_menu_for_today
from UserLogin import User
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), 'Class')))
from SQLConnect import create_connection
from Recommendation_System import RecommendationEngine
from Admin import Admin
from chef import Chef
from Employee import Employee  

class MenuSystem:
    def __init__(self, connection):
        self.connection = connection

    def display_menu(self, role_name, employee_id):
        if role_name == 'Admin':
            return self.admin_menu()
        elif role_name == 'Chef':
            return self.chef_menu()
        elif role_name == 'Employee':
            return self.user_menu(employee_id)
        else:
            return "Invalid role!"

    def admin_menu(self):
        while True:
            menu = [
                "Admin Menu:",
                "1. Add Menu Item",
                "2. Update Menu Item",
                "3. Delete Menu Item",
                "4. View Menu",
                "5. Exit"
            ]
            menu_display = "\n".join(menu)
            yield menu_display

    def execute_admin_command(self, choice, args):
        admin = Admin()
        if choice == '1':
            foodname, foodprice = args
            try:
                admin.add_food_item(foodname, foodprice)
                return "Food item added successfully."
            except Exception as e:
                return f"Error adding food item: {e}"
        elif choice == '2':
            foodid, foodname, foodprice = args
            try:
                admin.update_food_item(foodid, foodname, foodprice)
                return "Food item updated successfully."
            except Exception as e:
                return f"Error updating food item: {e}"
        elif choice == '3':
            foodid = args[0]
            try:
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
            return "Exit"
        else:
            return "Invalid choice!"

    def chef_menu(self):
        while True:
            menu = [
                "Chef Menu:",
                "1. Roll Out Menu for Next Day",
                "2. View Feedback",
                "3. Generate Monthly Feedback Report",
                "4. View Menu",
                "5. Send Final Menu for Today",
                "6. View Recommendation",
                "7. Exit"
            ]
            menu_display = "\n".join(menu)
            yield menu_display

    def execute_chef_command(self, choice, args):
        chef = Chef(None, None, None, None, None)
        if choice == '1':
            meal_type, food_item_id = args
            return chef.roll_out_menu(self.connection, meal_type, food_item_id)
        elif choice == '2':
            return chef.view_feedback(self.connection)
        elif choice == '3':
            return chef.generate_report(self.connection)
        elif choice == '4':
            return self.view_menu()
        elif choice == '5':
            meal_type, food_item_id = args
            return chef.send_final_menu(self.connection, meal_type, food_item_id)
        elif choice == '6':
            return  view_rolled_out_menu_for_today(self.connection)
        elif choice == '7':
            engine = RecommendationEngine(self.connection)
            return engine.recommend_items(top_n=5) 
        elif choice == '8':
            return "Exit"
        else:
            return "Invalid choice!"

    def user_menu(self, employee_id):
        while True:
            menu = [
                "User Menu:",
                "1. View Menu",
                "2. Select Food Item",
                "3. Give Feedback",
                "4. Exit"
            ]
            menu_display = "\n".join(menu)
            yield menu_display

    def execute_user_command(self, choice, employee_id, args):
        if choice == '1':
            return Employee.view_menu(self.connection, availability_only=True)
        elif choice == '2':
            food_item_id = int(args[0])
            return Employee.select_food_item(self.connection, employee_id, food_item_id)
        elif choice == '3':
            food_item_id, comment, rating = args
            return Employee.give_feedback(self.connection, employee_id, food_item_id, comment, rating)
        elif choice == '4':
            return  view_rolled_out_menu_for_today(self.connection)
        elif choice == '5':
            return "Exit"
        else:
            return "Invalid choice!"

    def view_menu(self, availability_only=False):
        return Employee.view_menu(self.connection, availability_only)

def App_run():
    connection = create_connection()
    menu_system = MenuSystem(connection)
    role, employee_id = User.verify_employee()
    menu_system.display_menu(role, employee_id)

if __name__ == "__main__":
    App_run()
