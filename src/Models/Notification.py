from datetime import datetime
import os
import sys
import mysql.connector
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from Database.SQLConnect import *

EMPLOYEE_ID = '1005'
DB_CONFIG = {
    'host': "localhost",
    'user': "root",
    'password': "Harshitha@555",
    'database': "cafeteriadb"
}
IS_READ_FALSE = 0

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

class Notification:
    @staticmethod
    def get_unread_notifications(connection, employee_id):
        cursor = connection.cursor()
        try:
            fetch_notifications_query = """
            SELECT Message 
            FROM notification 
            WHERE UserID = (SELECT UserID FROM user WHERE EmployeeID = %s) 
            AND IsRead = %s
            """
            cursor.execute(fetch_notifications_query, (employee_id, IS_READ_FALSE))
            notifications = cursor.fetchall()
            
            if notifications:
                update_notifications_query = """
                UPDATE notification 
                SET IsRead = 1 
                WHERE UserID = (SELECT UserID FROM user WHERE EmployeeID = %s) 
                AND IsRead = %s
                """
                cursor.execute(update_notifications_query, (employee_id, IS_READ_FALSE))
                connection.commit()
                
            return [notification[0] for notification in notifications]
        
        except mysql.connector.Error as e:
            print(f"Error fetching notifications: {e}")
            return []

    @staticmethod
    def send_notification_to_all_users(connection, message, dietary_type=None):
        cursor = connection.cursor()
        try:
            select_users_query = """
            SELECT u.UserID, u.dietary_preference
            FROM user u
            JOIN role r ON u.RoleID = r.RoleID 
            WHERE r.RoleName = 'Employee'
            """
            cursor.execute(select_users_query)
            users = cursor.fetchall()

            today_date = datetime.today().strftime('%Y-%m-%d')
            for user in users:
                user_id, dietary_preference = user
                insert_notification_query = """
                INSERT INTO notification (Message, NotificationDate, IsRead, UserID) 
                VALUES (%s, %s, %s, %s)
                """
                cursor.execute(insert_notification_query, (message, today_date, IS_READ_FALSE, user_id))
            
            connection.commit()
        
        except mysql.connector.Error as e:
            print(f"Error inserting notification: {e}")

def main():
    try:
        connection = mysql.connector.connect(**DB_CONFIG)

        unread_notifications = Notification.get_unread_notifications(connection, EMPLOYEE_ID)
        print(f"Unread notifications for employee {EMPLOYEE_ID}: {unread_notifications}")

        message = "This is a test notification"
        Notification.send_notification_to_all_users(connection, message)
        print("Notification sent to all users.")

    except mysql.connector.Error as e:
        print(f"Error connecting to MySQL: {e}")

    finally:
        if connection.is_connected():
            connection.close()
            print("MySQL connection closed.")

if __name__ == "__main__":
    main()
