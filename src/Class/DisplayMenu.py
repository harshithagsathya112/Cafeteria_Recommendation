import os
import sys
from User import User, run
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from SQLConnect import create_connection
from Admin import Admin
from chef import Chef
from datetime import datetime, timedelta

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
            admin.add_food_item(foodname, foodprice)
            return "Food item added successfully."
        elif choice == '2':
            foodid, foodname, foodprice = args
            admin.update_food_item(foodid, foodname, foodprice)
            return "Food item updated successfully."
        elif choice == '3':
            foodid = args[0]
            admin.delete_food_item(foodid)
            return "Food item deleted successfully."
        elif choice == '4':
            return admin.get_food_items()
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
                "6. Exit"
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
            return self.view_menu(availability_only=True)
        elif choice == '2':
            food_item_id = int(args[0])
            return self.select_food_item(employee_id, food_item_id)
        elif choice == '3':
            food_item_id, comment, rating = args
            return self.give_feedback(employee_id, food_item_id, comment, rating)
        elif choice == '4':
            return "Exit"
        else:
            return "Invalid choice!"

    def view_menu(self, availability_only=False):
        cursor = self.connection.cursor()
        if availability_only:
            cursor.execute("SELECT * FROM fooditem WHERE AvailabilityStatus = 1")
        else:
            cursor.execute("SELECT * FROM fooditem")
        result = cursor.fetchall()
        menu = ["Menu:"]
        for row in result:
            menu.append(f"ID: {row[0]}, Name: {row[1]}, Price: {row[2]}, Available: {row[3]}")
        return "\n".join(menu)

    def select_food_item(self, employee_id, food_item_id):
        cursor = self.connection.cursor()
        cursor.execute("SELECT UserID FROM user WHERE EmployeeID = %s", (employee_id,))
        result = cursor.fetchone()
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
                self.connection.commit()
                return "Your food item selection has been recorded."
        else:
            return "No menu items rolled out today."

    def give_feedback(self, employee_id, food_item_id, comment, rating):
        cursor = self.connection.cursor()
        cursor.execute("SELECT UserID FROM user WHERE EmployeeID = %s", (employee_id,))
        result = cursor.fetchone()
        userid = result[0]
        
        cursor.execute("INSERT INTO feedback (UserID, Comment, Rating, FeedbackDate, FoodItemID) VALUES (%s, %s, %s, CURDATE(), %s)", 
                       (userid, comment, rating, food_item_id))
        self.connection.commit()
        return "Feedback submitted successfully."

def App_run():
    connection = create_connection()
    menu_system = MenuSystem(connection)
    role, employee_id = run()
    menu_system.display_menu(role, employee_id)

if __name__ == "__main__":
    App_run()
