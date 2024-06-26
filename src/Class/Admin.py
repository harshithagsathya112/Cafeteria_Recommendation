import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from SQLConnect import create_connection

class Admin:
    def __init__(self):
        self.connection = create_connection()
        self.cursor = self.connection.cursor()

    def add_food_item(self, item_name, price):
        try:
            sql = "INSERT INTO fooditem_main (ItemName, Price) VALUES (%s, %s)"
            values = (item_name, price)
            self.cursor.execute(sql, values)
            self.connection.commit()
            print(f"Food item added with ID: {self.cursor.lastrowid}")
            return self.cursor.lastrowid
        except Exception as e:
            print(f"Error adding food item: {e}")

    def update_food_item(self, food_item_id, item_name=None, price=None):
        try:
            updates = []
            values = []

            if item_name:
                updates.append("ItemName = %s")
                values.append(item_name)
            if price:
                updates.append("Price = %s")
                values.append(price)

            if updates:
                sql = f"UPDATE fooditem_main SET {', '.join(updates)} WHERE LookupID = %s"
                values.append(food_item_id)
                self.cursor.execute(sql, values)
                self.connection.commit()
                print(f"Food item with ID: {food_item_id} updated")
        except Exception as e:
            print(f"Error updating food item: {e}")

    def delete_food_item(self, food_item_id):
        try:
            sql = "DELETE FROM fooditem_main WHERE LookupID = %s"
            self.cursor.execute(sql, (food_item_id,))
            self.connection.commit()
            print(f"Food item with ID: {food_item_id} deleted")
        except Exception as e:
            print(f"Error deleting food item: {e}")

    def get_food_items(self):
        try:
            self.cursor.execute("SELECT * FROM fooditem_main")
            result = self.cursor.fetchall()
            for row in result:
                print(row)
        except Exception as e:
            print(f"Error fetching food items: {e}")

    def close_connection(self):
        try:
            self.cursor.close()
            self.connection.close()
            print("Database connection closed")
        except Exception as e:
            print(f"Error closing connection: {e}")

'''# Usage example
if __name__ == "__main__":
    admin = Admin()

    # Adding a food item
    id = admin.add_food_item(item_name="Salad1", price=10.99)

    # Updating a food item
    admin.update_food_item(food_item_id=id, price=12.99)

    # Deleting a food item
    admin.delete_food_item(food_item_id=id)

    # Fetching all food items
    admin.get_food_items()

    # Closing the database connection
    admin.close_connection()'''
