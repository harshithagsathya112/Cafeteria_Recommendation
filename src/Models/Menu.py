from datetime import datetime, timedelta
import os
import sys
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(project_root)
from Models.Notification import Notification  

class MenuManager:
    def __init__(self, connection):
        self.connection = connection

    def fetch_user_preference(self, employee_id):
        cursor = self.connection.cursor()
        cursor.execute("SELECT RoleName FROM role JOIN user ON role.RoleID = user.RoleID WHERE user.EmployeeID = %s", (employee_id,))
        role = cursor.fetchone()
        
        if not role:
            return None, None
        
        role_name = role[0]

        if role_name != "Chef":
            cursor.execute("SELECT dietary_preference, spice_level, preferred_cuisine, sweet_tooth FROM user WHERE EmployeeID = %s", (employee_id,))
            user_details = cursor.fetchone()
            if not user_details:
                return None, None
            return role_name, user_details
        else:
            return role_name, None

    def roll_out_menu(self, meal_type, food_item_id):
        try:
            date = (datetime.today() - timedelta(days=1)).strftime('%Y-%m-%d')

            cursor = self.connection.cursor()
            cursor.execute("INSERT INTO menu (Date, MealType, FoodItemID) VALUES (%s, %s, %s)", 
                           (date, meal_type, food_item_id))
            cursor.execute("SELECT ItemName FROM fooditem WHERE FoodItemID = %s", (food_item_id,))
            food_name = cursor.fetchone()[0]
            self.notify_users_about_menu(food_name)
            self.connection.commit()
            return "Menu rolled out for the next day."
        except Exception as e:
            return f"Error rolling out menu: {e}"

    def view_rolled_out_menu_for_today(self, employee_id):
        try:
            role_name, user_details = self.fetch_user_preference(employee_id)

            if not role_name:
                return "Role not found."

            if role_name != "Chef":
                dietary_preference, spice_level, preferred_cuisine, sweet_tooth = user_details
            else:
                dietary_preference, spice_level, preferred_cuisine, sweet_tooth = None, None, None, None

            previous_date = (datetime.today() - timedelta(days=1)).strftime('%Y-%m-%d')
            menu_items = self.fetch_rolled_out_menu_items(previous_date)

            if not menu_items:
                return "No menu items rolled out for today."

            if role_name != "Chef":
                menu_items = self.sort_menu_items(menu_items, dietary_preference, spice_level, preferred_cuisine, sweet_tooth)

            return self.format_menu_output(menu_items)

        except Exception as e:
            return f"Error fetching today's rolled-out menu: {e}"

    def fetch_rolled_out_menu_items(self, date):
        cursor = self.connection.cursor()
        query_for_fetching_rolledout_menu = """
            SELECT menu.FoodItemID, fooditem.ItemName, fooditem.Price, menu.MealType, fooditem.dietary_type, fooditem.spice_level, fooditem.cuisine, fooditem.is_sweet
            FROM menu
            JOIN fooditem ON menu.FoodItemID = fooditem.FoodItemID
            WHERE menu.Date = %s
        """
        cursor.execute(query_for_fetching_rolledout_menu, (date,))
        return cursor.fetchall()
    
    def update_menu_and_availability_status(self, meal_type, food_item_id):
        try:
            today_date = datetime.today().strftime('%Y-%m-%d')
            previous_date = (datetime.today() - timedelta(days=1)).strftime('%Y-%m-%d')
            day_before_previous_date = (datetime.today() - timedelta(days=2)).strftime('%Y-%m-%d')
            notification = Notification()
            cursor = self.connection.cursor()

            cursor.execute("SELECT COUNT(*) FROM menu WHERE Date = %s AND FoodItemID = %s", (previous_date, food_item_id))
            count_fooditem_availability = cursor.fetchone()[0]

            if count_fooditem_availability == 0:
                cursor.execute("INSERT INTO menu (Date, MealType, FoodItemID, FinalFlag) VALUES (%s, %s, %s, %s)",
                               (previous_date, meal_type, food_item_id, 1))
            else:
                cursor.execute("UPDATE menu SET FinalFlag = %s WHERE Date = %s AND FoodItemID = %s", (1, previous_date, food_item_id))

            self.connection.commit()

            cursor.execute("SELECT FoodItemID FROM menu WHERE Date = %s AND FinalFlag = 1", (previous_date,))
            food_items_with_final_flag = cursor.fetchall()

            for item in food_items_with_final_flag:
                cursor.execute("UPDATE fooditem SET AvailabilityStatus = %s WHERE FoodItemID = %s", 
                               (1, item[0]))

                cursor.execute("SELECT ItemName FROM fooditem WHERE FoodItemID = %s", (item[0],))
                food_name = cursor.fetchone()[0]
                User_Notification_message = f"{food_name} is now available."
                notification.send_notification_to_all_users(self.connection, User_Notification_message)

            cursor.execute("UPDATE fooditem SET AvailabilityStatus = %s WHERE FoodItemID NOT IN (SELECT FoodItemID FROM menu WHERE Date = %s AND FinalFlag = 1)", 
                           (0, previous_date))

            self.connection.commit()
            return "Food item is added for today's menu."
        except Exception as e:
            return f"Error updating menu and availability status: {e}"


    def sort_menu_items(self, menu_items, dietary_preference, spice_level, preferred_cuisine, sweet_tooth):
        def sort_key(item):
            score = 0
            if dietary_preference == item[4]:
                score += 40
            if spice_level == item[5]:
                score += 5
            if preferred_cuisine == item[6]:
                score += 3
            if sweet_tooth and item[7]:
                score += 10
            return score

        return sorted(menu_items, key=sort_key, reverse=True)

    def format_menu_output(self, menu_items):
        Formated_menu_items = ["Rolled Out Menu for Today:"]
        for item in menu_items:
            Formated_menu_items.append(f"ID: {item[0]}, Name: {item[1]}, Price: {item[2]}, Meal Type: {item[3]}")
        return "\n".join(Formated_menu_items)

    def notify_users_about_menu(self, food_name):
        notification = Notification()
        Notification_message_for_user = f"{food_name} has been added to the rolled-out menu."
        notification.send_notification_to_all_users(self.connection,Notification_message_for_user)

    
