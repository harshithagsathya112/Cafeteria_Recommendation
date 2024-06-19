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

        # Check if the food item is already in the previous day's menu
        cursor.execute("SELECT COUNT(*) FROM menu WHERE Date = %s AND FoodItemID = %s", (previous_date, food_item_id))
        count = cursor.fetchone()[0]

        # If the food item is not in the previous day's menu, add it
        if count == 0:
            cursor.execute("INSERT INTO menu (Date, MealType, FoodItemID, FinalFlag) VALUES (%s, %s, %s, %s)",
                           (previous_date, meal_type, food_item_id, 1))
        else:
            # Update FinalFlag for the existing food item
            cursor.execute("UPDATE menu SET FinalFlag = %s WHERE Date = %s AND FoodItemID = %s", (1, previous_date, food_item_id))
        
        connection.commit()

        # Check if the final flag is set for the food item on Previous's date
        cursor.execute("SELECT FoodItemID FROM menu WHERE Date = %s AND FinalFlag = 1", (previous_date,))
        food_items_with_final_flag = cursor.fetchall()

        # Set availability status of these food items to 1
        for item in food_items_with_final_flag:
            cursor.execute("UPDATE fooditem SET AvailabilityStatus = %s WHERE FoodItemID = %s", 
                           (1, item[0]))
            
            cursor.execute("SELECT ItemName FROM fooditem WHERE FoodItemID = %s", (item[0],))
            food_name = cursor.fetchone()[0]
            message = f"{food_name} is now available."
            insert_notification_for_all_users(message)

        # Set availability status of food items not in the previous day's menu to 0
        cursor.execute("UPDATE fooditem SET AvailabilityStatus = %s WHERE FoodItemID NOT IN (SELECT FoodItemID FROM menu WHERE Date = %s AND FinalFlag = 1)", 
                       (0, previous_date))
        
        cursor.execute("SELECT FoodItemID FROM menu WHERE Date = %s AND FinalFlag = 1", (previous_date,))
        previous_day_final_menu = set(item[0] for item in cursor.fetchall())

        cursor.execute("SELECT FoodItemID FROM menu WHERE Date = %s AND FinalFlag = 1", (day_before_previous_date,))
        day_before_previous_final_menu = set(item[0] for item in cursor.fetchall())

        # Find changes in availability status
        newly_available = previous_day_final_menu - day_before_previous_final_menu
        newly_unavailable = day_before_previous_final_menu - previous_day_final_menu

        
        
        connection.commit()
        return "Final flag updated for previous day's menu items and availability statuses updated."

def view_rolled_out_menu_for_today(connection):
        try:
            cursor = connection.cursor()
            previous_date = (datetime.today() - timedelta(days=1)).strftime('%Y-%m-%d')
            query = """
            SELECT menu.FoodItemID, fooditem.ItemName, fooditem.Price, menu.MealType
            FROM menu
            JOIN fooditem ON menu.FoodItemID = fooditem.FoodItemID
            WHERE menu.Date = %s
            """
            cursor.execute(query, (previous_date,))
            result = cursor.fetchall()
            if result:
                rolled_out_menu = ["Rolled Out Menu for Today:"]
                for row in result:
                    rolled_out_menu.append(f"ID: {row[0]}, Name: {row[1]}, Price: {row[2]}, Meal Type: {row[3]}")
                return "\n".join(rolled_out_menu)
            else:
                return "No menu items rolled out for today."
        except Exception as e:
            return f"Error fetching today's rolled-out menu: {e}"