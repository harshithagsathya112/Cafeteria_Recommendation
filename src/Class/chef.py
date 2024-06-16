from datetime import datetime, timedelta

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

        cursor = connection.cursor()
        # Update FinalFlag for previous day's menu items
        cursor.execute("UPDATE menu SET FinalFlag = %s WHERE Date = %s AND FoodItemID = %s", (1, previous_date, food_item_id))
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
        return "Final flag updated for previous day's menu items and availability statuses updated."
