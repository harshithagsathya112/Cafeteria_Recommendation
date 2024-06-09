
from datetime import datetime, timedelta;
class Chef:
    def __init__(self, user_id, employee_id, name, role_id, password):
        self.user_id = user_id
        self.employee_id = employee_id
        self.name = name
        self.role_id = role_id
        self.password = password

    def roll_out_menu(self, connection):
        date = (datetime.today() - timedelta(days=1)).strftime('%Y-%m-%d')
        meal_type = input("Enter the meal type (e.g., breakfast, lunch, dinner): ")
        food_item_id = int(input("Enter the food item ID: "))
        
        cursor = connection.cursor()
        cursor.execute("INSERT INTO menu (Date, MealType, FoodItemID) VALUES (%s, %s, %s)", 
                       (date, meal_type, food_item_id))
        connection.commit()
        print("Menu rolled out for the next day.")

    def view_feedback(self, connection):
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM feedback")
        result = cursor.fetchall()
        print("Feedback:")
        for row in result:
            print(f"Feedback ID: {row[0]}, User ID: {row[1]}, Comment: {row[2]}, Rating: {row[3]}, Date: {row[4]}, Food Item ID: {row[5]}")
    
    def generate_report(self, connection):
        cursor = connection.cursor()
        cursor.execute("""
            SELECT FoodItemID, AVG(Rating) as avg_rating, COUNT(*) as feedback_count
            FROM feedback
            GROUP BY FoodItemID
            """)
        result = cursor.fetchall()
        print("Monthly Feedback Report:")
        for row in result:
            print(f"Food Item ID: {row[0]}, Average Rating: {row[1]}, Feedback Count: {row[2]}")
    
    def send_final_menu(self, connection):
        today_date = datetime.today().strftime('%Y-%m-%d')
        previous_date = (datetime.today() - timedelta(days=1)).strftime('%Y-%m-%d')
        meal_type = input("Enter the meal type (e.g., breakfast, lunch, dinner): ")
        food_item_id = int(input("Enter the food item ID: "))

        cursor = connection.cursor()
        # Update FinalFlag for previous day's menu items
        cursor.execute("UPDATE menu SET FinalFlag = %s WHERE Date = %s AND FoodItemID = %s", (1, previous_date,food_item_id))
        connection.commit()

        # Check if the final flag is set for the food item on Previous's date
        cursor.execute("SELECT FoodItemID FROM menu WHERE Date = %s AND FinalFlag = 1", (previous_date,))
        food_items_with_final_flag = cursor.fetchall()

        # Set availability status of these food items to 1
        for item in food_items_with_final_flag:
            cursor.execute("UPDATE fooditem SET AvailabilityStatus = %s WHERE FoodItemID = %s", 
                           (1, item[0]))

        # Set availability status of food items not in the previous day's menu to 0
        cursor.execute("UPDATE fooditem SET AvailabilityStatus = %s WHERE FoodItemID NOT IN (SELECT FoodItemID FROM menu WHERE Date = %s AND FinalFlag = 1)", 
                       (0, previous_date))
        connection.commit()
        print("Final flag updated for previous day's menu items and availability statuses updated.")