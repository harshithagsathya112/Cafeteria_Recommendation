from datetime import datetime
import os,sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from SQLConnect import create_connection,execute_read_query,execute_query
def get_notifications(employee_id):
    connection = create_connection()
    query = f"SELECT Message FROM notification WHERE UserID = (SELECT UserID FROM user WHERE EmployeeID = '{employee_id}') AND IsRead = 0"
    notifications = execute_read_query(connection, query)
    if notifications:
        update_query = f"UPDATE notification SET IsRead = 1 WHERE UserID = (SELECT UserID FROM user WHERE EmployeeID = '{employee_id}') AND IsRead = 0"
        execute_query(connection, update_query)
    return [notification[0] for notification in notifications]

def insert_notification_for_all_users(message,dietary_type=None):
    connection = create_connection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT u.UserID ,u.dietary_preference
        FROM user u
        JOIN role r ON u.RoleID = r.RoleID 
        WHERE r.RoleName = 'Employee'
    """)
    users = cursor.fetchall()

    today_date = datetime.today().strftime('%Y-%m-%d')
    for user in users:
        user_id, dietary_preference = user
        if dietary_type is None:
            cursor.execute("INSERT INTO notification (Message, NotificationDate, IsRead, UserID) VALUES (%s, %s, %s, %s)",
                           (message, today_date, 0, user_id))
        elif dietary_type.lower() == 'vegetarian' and dietary_preference.lower() == 'vegetarian':
            cursor.execute("INSERT INTO notification (Message, NotificationDate, IsRead, UserID) VALUES (%s, %s, %s, %s)",
                           (message, today_date, 0, user_id))

        else :
            cursor.execute("INSERT INTO notification (Message, NotificationDate, IsRead, UserID) VALUES (%s, %s, %s, %s)",
                           (message, today_date, 0, user_id))
    connection.commit()
    connection.close()

if __name__ == "__main__":
    insert_notification_for_all_users("Test notification message for all users.")
