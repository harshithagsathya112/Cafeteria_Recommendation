from datetime import datetime
import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from Database.SQLConnect import execute_read_query, execute_query

class Notification:
    @staticmethod
    def get_unread_notifications(connection, employee_id):
        cursor = connection.cursor()
        try:
            query_select = """
            SELECT Message 
            FROM notification 
            WHERE UserID = (SELECT UserID FROM user WHERE EmployeeID = %s) 
            AND IsRead = 0
            """
            cursor.execute(query_select, (employee_id,))
            notifications = cursor.fetchall()
            
            if notifications:
                update_query = f"UPDATE notification SET IsRead = 1 WHERE UserID = (SELECT UserID FROM user WHERE EmployeeID = '{employee_id}') AND IsRead = 0"
                execute_query(connection, update_query)
            return [notification[0] for notification in notifications]
        except Exception as e:
            print(f"Error fetching notifications: {e}")
            return []

    @staticmethod
    def send_notification_to_all_users(connection, message, dietary_type=None):
        """Send a notification to all employees."""
        try:
            cursor = connection.cursor()

            query = """
                SELECT u.UserID, u.dietary_preference
                FROM user u
                JOIN role r ON u.RoleID = r.RoleID 
                WHERE r.RoleName = 'Employee'
            """
            cursor.execute(query)
            users = cursor.fetchall()

            today_date = datetime.today().strftime('%Y-%m-%d')
            for user in users:
                user_id, dietary_preference = user
                insert_query = """
                    INSERT INTO notification (Message, NotificationDate, IsRead, UserID) 
                    VALUES (%s, %s, %s, %s)
                """
                cursor.execute(insert_query, (message, today_date, 0, user_id))
            
            connection.commit()
        except Exception as e:
            print(f"Error inserting notification: {e}")


