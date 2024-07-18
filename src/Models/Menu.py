from datetime import datetime, timedelta
import os
import sys
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(project_root)

from Models.Notification import Notification

DIETARY_PREFERENCE_SCORE = 40
SPICE_LEVEL_SCORE = 5
PREFERRED_CUISINE_SCORE = 3
SWEET_TOOTH_SCORE = 10

ROLE_CHEF = "Chef"
DATE_FORMAT = '%Y-%m-%d'
FINAL_FLAG = 1
AVAILABLE = 1
NOT_AVAILABLE = 0

FOOD_ITEM_ID_IDX = 0
ITEM_NAME_IDX = 1
PRICE_IDX = 2
MEAL_TYPE_IDX = 3
DIETARY_TYPE_IDX = 4
SPICE_LEVEL_IDX = 5
CUISINE_IDX = 6
IS_SWEET_IDX = 7

class MenuManager:
    def __init__(self, connection):
        self.connection = connection

    def fetch_user_preference(self, employee_id):
        cursor = self.connection.cursor()
        SQL_FETCH_ROLE = """
        SELECT RoleName 
        FROM role 
        JOIN user ON role.RoleID = user.RoleID 
        WHERE user.EmployeeID = %s
        """
        cursor.execute(SQL_FETCH_ROLE, (employee_id,))
        role = cursor.fetchone()
        
        if not role:
            return None, None
        
        role_name = role[0]

        if role_name != ROLE_CHEF:
            SQL_FETCH_USER_DETAILS = """
            SELECT dietary_preference, spice_level, preferred_cuisine, sweet_tooth 
            FROM user 
            WHERE EmployeeID = %s
            """
            cursor.execute(SQL_FETCH_USER_DETAILS, (employee_id,))
            user_details = cursor.fetchone()
            if not user_details:
                return None, None
            return role_name, user_details
        else:
            return role_name, None

    def roll_out_menu(self, meal_type, food_item_id):
        try:
            date = (datetime.today() - timedelta(days=1)).strftime(DATE_FORMAT)

            cursor = self.connection.cursor()
            SQL_INSERT_MENU = """
            INSERT INTO menu (Date, MealType, FoodItemID) 
            VALUES (%s, %s, %s)
            """
            cursor.execute(SQL_INSERT_MENU, (date, meal_type, food_item_id))
            
            SQL_FETCH_ITEM_NAME = "SELECT ItemName FROM fooditem WHERE FoodItemID = %s"
            cursor.execute(SQL_FETCH_ITEM_NAME, (food_item_id,))
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

            dietary_preference, spice_level, preferred_cuisine, sweet_tooth = (None, None, None, None)
            if role_name != ROLE_CHEF:
                dietary_preference, spice_level, preferred_cuisine, sweet_tooth = user_details

            previous_date = (datetime.today() - timedelta(days=1)).strftime(DATE_FORMAT)
            
            SQL_FETCH_ROLLED_OUT_MENU_ITEMS = """
            SELECT menu.FoodItemID, fooditem.ItemName, fooditem.Price, menu.MealType, 
            fooditem.dietary_type, fooditem.spice_level, fooditem.cuisine, fooditem.is_sweet
            FROM menu
            JOIN fooditem ON menu.FoodItemID = fooditem.FoodItemID
            WHERE menu.Date = %s
            """
            cursor = self.connection.cursor()
            cursor.execute(SQL_FETCH_ROLLED_OUT_MENU_ITEMS, (previous_date,))
            menu_items = cursor.fetchall()

            if not menu_items:
                return "No menu items rolled out for today."

            if role_name != ROLE_CHEF:
                menu_items = self.sort_menu_items(menu_items, dietary_preference, spice_level, preferred_cuisine, sweet_tooth)

            return self.format_menu_output(menu_items)

        except Exception as e:
            return f"Error fetching today's rolled-out menu: {e}"

    def update_menu_and_availability_status(self, meal_type, food_item_id):
        try:
            today_date = datetime.today().strftime(DATE_FORMAT)
            previous_date = (datetime.today() - timedelta(days=1)).strftime(DATE_FORMAT)
            notification = Notification()
            cursor = self.connection.cursor()

            SQL_CHECK_MENU_AVAILABILITY = "SELECT COUNT(*) FROM menu WHERE Date = %s AND FoodItemID = %s"
            cursor.execute(SQL_CHECK_MENU_AVAILABILITY, (previous_date, food_item_id))
            count_fooditem_availability = cursor.fetchone()[0]

            if count_fooditem_availability == 0:
                SQL_INSERT_MENU_WITH_FINAL_FLAG = """
                INSERT INTO menu (Date, MealType, FoodItemID, FinalFlag) 
                VALUES (%s, %s, %s, %s)
                """
                cursor.execute(SQL_INSERT_MENU_WITH_FINAL_FLAG, (previous_date, meal_type, food_item_id, FINAL_FLAG))
            else:
                SQL_UPDATE_MENU_FINAL_FLAG = """
                UPDATE menu 
                SET FinalFlag = %s 
                WHERE Date = %s AND FoodItemID = %s
                """
                cursor.execute(SQL_UPDATE_MENU_FINAL_FLAG, (FINAL_FLAG, previous_date, food_item_id))
            
            self.connection.commit()

            SQL_FETCH_ITEM_NAME = "SELECT ItemName FROM fooditem WHERE FoodItemID = %s"
            cursor.execute(SQL_FETCH_ITEM_NAME, (food_item_id,))
            food_name = cursor.fetchone()[0]
            notification_message = f"{food_name} is now available."
            notification.send_notification_to_all_users(self.connection, notification_message)

            SQL_FETCH_ITEMS_WITH_FINAL_FLAG = "SELECT FoodItemID FROM menu WHERE Date = %s AND FinalFlag = 1"
            cursor.execute(SQL_FETCH_ITEMS_WITH_FINAL_FLAG, (previous_date,))
            food_items_with_final_flag = cursor.fetchall()

            SQL_UPDATE_FOOD_AVAILABILITY = """
            UPDATE fooditem 
            SET AvailabilityStatus = %s 
            WHERE FoodItemID = %s
            """

            for item in food_items_with_final_flag:
                cursor.execute(SQL_UPDATE_FOOD_AVAILABILITY, (AVAILABLE, item[FOOD_ITEM_ID_IDX]))

            SQL_UPDATE_FOOD_NOT_AVAILABLE = """
            UPDATE fooditem 
            SET AvailabilityStatus = %s 
            WHERE FoodItemID NOT IN (
            SELECT FoodItemID FROM menu WHERE Date = %s AND FinalFlag = %s
            )
            """
            cursor.execute(SQL_UPDATE_FOOD_NOT_AVAILABLE, (NOT_AVAILABLE, previous_date, FINAL_FLAG))

            self.connection.commit()
            return "Food item is added for today's menu."
        except Exception as e:
            return f"Error updating menu and availability status: {e}"

    def sort_menu_items(self, menu_items, dietary_preference, spice_level, preferred_cuisine, sweet_tooth):
        def sort_key(item):
            score = 0
            if dietary_preference == item[DIETARY_TYPE_IDX]:
                score += DIETARY_PREFERENCE_SCORE
            if spice_level == item[SPICE_LEVEL_IDX]:
                score += SPICE_LEVEL_SCORE
            if preferred_cuisine == item[CUISINE_IDX]:
                score += PREFERRED_CUISINE_SCORE
            if sweet_tooth and item[IS_SWEET_IDX]:
                score += SWEET_TOOTH_SCORE
            return score

        return sorted(menu_items, key=sort_key, reverse=True)

    def format_menu_output(self, menu_items):
        formatted_menu_items = ["Rolled Out Menu for Today:"]
        for item in menu_items:
            formatted_menu_items.append(f"ID: {item[FOOD_ITEM_ID_IDX]}, Name: {item[ITEM_NAME_IDX]}, Price: {item[PRICE_IDX]}, Meal Type: {item[MEAL_TYPE_IDX]}")
        return "\n".join(formatted_menu_items)

    def notify_users_about_menu(self, food_name):
        notification = Notification()
        notification_message = f"{food_name} has been added to the rolled-out menu."
        notification.send_notification_to_all_users(self.connection, notification_message)
