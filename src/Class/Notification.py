from datetime import datetime
import os,sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from SQLConnect import create_connection


def insert_notification_for_all_users(message):
    connection = create_connection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT u.UserID 
        FROM user u
        JOIN role r ON u.RoleID = r.RoleID 
        WHERE r.RoleName = 'Employee'
    """)
    users = cursor.fetchall()

    today_date = datetime.today().strftime('%Y-%m-%d')
    for user in users:
        cursor.execute("INSERT INTO notification (Message, NotificationDate, IsRead, UserID) VALUES (%s, %s, %s, %s)",
                       (message, today_date, 0, user[0]))

    connection.commit()
    connection.close()

if __name__ == "__main__":
    insert_notification_for_all_users("Test notification message for all users.")
