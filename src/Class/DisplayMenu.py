import os
import sys
from User import User,run
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from SQLConnect import create_connection
from User import run
from Admin import Admin
from chef import Chef


class MenuSystem:
    def __init__(self, connection):
        self.connection = connection

    def display_menu(self, role_name,EmployeeId):
        if role_name == 'Admin':
            self.admin_menu()
        elif role_name == 'Chef':
            self.chef_menu()
        elif role_name == 'Employee':
            self.user_menu(EmployeeId)
        else:
            print("Invalid role!")

    def admin_menu(self):
        while True:
            print("Admin Menu:")
            print("1. Add Menu Item")
            print("2. Update Menu Item")
            print("3. Delete Menu Item")
            print("4. View Menu")
            print("5. Exit")
            admin = Admin()
            choice = input("Select an option: ")
            if choice == '1':
                foodname = input("Enter food name: ")
                foodprice = input("Enter food price: ")
                admin.add_food_item(foodname, foodprice)
            elif choice == '2':
                foodid = input("Enter food id: ")
                foodname = input("Enter food name: ")
                foodprice = input("Enter food price: ")
                admin.update_food_item(foodid, foodname, foodprice)
            elif choice == '3':
                foodid = input("Enter food id: ")
                admin.delete_food_item(foodid)
            elif choice == '4':
                admin.get_food_items()
            elif choice == '5':
                break
            else:
                print("Invalid choice!")

    def chef_menu(self):
        while True:
            print("Chef Menu:")
            print("1. Roll Out Menu for Next Day")
            print("2. View Feedback")
            print("3. Generate Monthly Feedback Report")
            print("4. View Menu")
            print("5. send final menu for today")
            print("6. Exit")
            chef = Chef(None, None, None, None, None)
            choice = input("Select an option: ")
            if choice == '1':
                chef.roll_out_menu(self.connection)
            elif choice == '2':
                chef.view_feedback(self.connection)
            elif choice == '3':
                chef.generate_report(self.connection)
            elif choice == '4':
                self.view_menu()
            elif choice == '5':
                chef.send_final_menu(self.connection)
            elif choice == '6':
                break
            else:
                print("Invalid choice!")

    def user_menu(self,EmployeeId):
        while True:
            print("User Menu:")
            print("1. View Menu")
            print("2. Select Food Item")
            print("3. Give Feedback")
            print("4. Exit")
            choice = input("Select an option: ")
            if choice == '1':
                self.view_menu(availability_only=True)
            elif choice == '2':
                self.select_food_item()
            elif choice == '3':
                self.give_feedback(EmployeeId)
            elif choice == '4':
                break
            else:
                print("Invalid choice!")

    def view_menu(self, availability_only=False):
        cursor = self.connection.cursor()
        if availability_only:
            cursor.execute("SELECT * FROM fooditem WHERE AvailabilityStatus = 1")
        else:
            cursor.execute("SELECT * FROM fooditem")
        result = cursor.fetchall()
        print("Menu:")
        for row in result:
            print(f"ID: {row[0]}, Name: {row[1]}, Price: {row[2]}, Available: {row[3]}, Lookup ID: {row[4]}")

    def select_food_item(self):
        user_id = int(input("Enter your user ID: "))
        food_item_id = int(input("Enter food item ID to select: "))
        
        cursor = self.connection.cursor()
        cursor.execute("INSERT INTO menu (Date, MealType, FoodItemID) VALUES (CURDATE(), 'lunch', %s)", 
                       (food_item_id,))
        self.connection.commit()
        print("Food item selected.")

    def give_feedback(self,EmployeeId):
        cursor = self.connection.cursor()
        cursor.execute("SELECT UserID FROM user WHERE EmployeeID = %s", (EmployeeId,))
        result = cursor.fetchone()
        userid=result[0]
        food_item_id = int(input("Enter food item ID: "))
        comment = input("Enter your comment: ")
        rating = int(input("Enter your rating (1-5): "))
        
        cursor = self.connection.cursor()
        cursor.execute("INSERT INTO feedback (UserID, Comment, Rating, FeedbackDate, FoodItemID) VALUES (%s, %s, %s, CURDATE(), %s)", 
                       (userid, comment, rating, food_item_id))
        self.connection.commit()
        print("Feedback submitted successfully.")

def App_run():
    connection = create_connection()
    menu_system = MenuSystem(connection)
    role,EmployeeId=run()
    menu_system.display_menu(role,EmployeeId)

if __name__ == "__main__":
    App_run()
    '''connection = create_connection()
    menu_system = MenuSystem(connection)
    role,EmployeeId=run()
    menu_system.display_menu(role,EmployeeId)'''
