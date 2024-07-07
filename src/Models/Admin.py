import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from Models.Notification import Notification

class Admin:
    def __init__(self,connection):
        self.connection = connection
        self.food_item_repository = FoodItemRepository(self.connection)
        self.notification_service = Notification()

    def add_food_item(self, item_name, price):
        try:
            food_item_id = self.food_item_repository.add_food_item(item_name, price)
            print(f"Food item added with ID: {food_item_id}")
            message = f"New food item '{item_name}' has been added."
            self.notification_service.send_notification_to_all_users(self.connection,message)
            return food_item_id
        except Exception as e:
            print(f"Error adding food item: {e}")
            raise

    def update_food_item(self, food_item_id, item_name=None, price=None):
        try:
            self.food_item_repository.update_food_item(food_item_id, item_name, price)
            print(f"Food item with ID: {food_item_id} updated")
        except Exception as e:
            print(f"Error updating food item: {e}")
            raise

    def delete_food_item(self, food_item_id):
        try:
            self.food_item_repository.delete_food_item(food_item_id)
            print(f"Food item with ID: {food_item_id} deleted")
        except Exception as e:
            print(f"Error deleting food item: {e}")
            raise

    def get_food_items(self):
        try:
            food_items = self.food_item_repository.get_food_items()
            menu = ["Menu:"]
            for row in food_items:
                menu.append(f"ID: {row[0]}, Name: {row[1]}, Price: {row[2]}")
            return "\n".join(menu)
        except Exception as e:
            print(f"Error fetching food items: {e}")
            raise

    def close_connection(self):
        try:
            self.food_item_repository.close()
            print("Database connection closed")
        except Exception as e:
            print(f"Error closing connection: {e}")
            raise

class FoodItemRepository:
    def __init__(self, connection):
        self.connection = connection
        self.cursor = self.connection.cursor()

    def add_food_item(self, item_name, price):
        sql = "INSERT INTO fooditem_main (ItemName, Price) VALUES (%s, %s)"
        values = (item_name, price)
        self.cursor.execute(sql, values)
        self.connection.commit()
        return self.cursor.lastrowid

    def update_food_item(self, food_item_id, item_name=None, price=None):
        updates = []
        values = []

        if item_name:
            updates.append("ItemName = %s")
            values.append(item_name)
        if price:
            updates.append("Price = %s")
            values.append(price)

        if updates:
            self.cursor.execute("SET SQL_SAFE_UPDATES = 0;")
            sql = f"UPDATE fooditem_main SET {', '.join(updates)} WHERE LookupID = %s"
            values.append(food_item_id)
            self.cursor.execute(sql, values)
            self.cursor.execute("SET SQL_SAFE_UPDATES = 1;")
            self.connection.commit()

    def delete_food_item(self, food_item_id):
        sql = "DELETE FROM fooditem_main WHERE LookupID = %s"
        self.cursor.execute(sql, (food_item_id,))
        self.connection.commit()

    def get_food_items(self):
        self.cursor.execute("SELECT * FROM fooditem_main")
        return self.cursor.fetchall()

    def close(self):
        self.cursor.close()
        self.connection.close()
