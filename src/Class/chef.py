

class Chef:
    def __init__(self, user_id, employee_id, name, role_id, password):
        self.user_id = user_id
        self.employee_id = employee_id
        self.name = name
        self.role_id = role_id
        self.password = password

    def roll_out_menu(self, connection):
        date = input("Enter the date for the menu (YYYY-MM-DD): ")
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
