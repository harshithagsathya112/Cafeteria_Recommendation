

from datetime import datetime
from SQLConnect import create_connection

def insert_notification_for_all_users(message):
    connection = create_connection()
    cursor = connection.cursor()

    cursor.execute("SELECT UserID FROM user")
    users = cursor.fetchall()

    # Insert notifications for all users
    today_date = datetime.today().strftime('%Y-%m-%d')
    for user in users:
        cursor.execute("INSERT INTO notification (Message, NotificationDate, IsRead, UserID) VALUES (%s, %s, %s, %s)",
                       (message, today_date, 0, user[0]))

    connection.commit()
    connection.close()

# Example usage
if __name__ == "__main__":
    insert_notification_for_all_users("Test notification message for all users.")
