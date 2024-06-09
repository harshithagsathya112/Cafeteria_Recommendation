import socket
import threading
import mysql.connector
from datetime import datetime
import queue

# Database setup
db_config = {
    'user': "root",
    'password': "Harshitha@555",
    'host': 'localhost',
    'database': "cafeteria"
}

# Server setup
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind(('localhost', 12345))
server_socket.listen(5)

clients = []
notification_queue = queue.Queue()

def fetch_unread_notifications():
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor()
    cursor.execute("SELECT NotificationID, Message FROM notification WHERE IsRead = 0")
    notifications = cursor.fetchall()
    cursor.close()
    conn.close()
    return notifications

def mark_notifications_as_read(notification_ids):
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor()
    for notification_id in notification_ids:
        cursor.execute("UPDATE notification SET IsRead = 1 WHERE NotificationID = %s", (notification_id,))
    conn.commit()
    cursor.close()
    conn.close()

def handle_client(client_socket, addr):
    print(f"Connection from {addr} has been established!")
    clients.append(client_socket)

    # Send unread notifications
    notifications = fetch_unread_notifications()
    notification_ids = []
    for notification_id, message in notifications:
        client_socket.send(message.encode())
        notification_ids.append(notification_id)
    
    if notification_ids:
        mark_notifications_as_read(notification_ids)

    try:
        while True:
            message = client_socket.recv(1024).decode()
            if message:
                print(f"Received message from {addr}: {message}")
                # Other message handling can be added here
    except:
        print(f"Connection from {addr} has been closed.")
    finally:
        clients.remove(client_socket)
        client_socket.close()

def broadcast_notifications():
    while True:
        notification = notification_queue.get()
        for client in clients:
            try:
                client.send(notification.encode())
            except:
                clients.remove(client)
        notification_queue.task_done()

print("Server started and listening on port 12345")

# Start the broadcast notification thread
broadcast_thread = threading.Thread(target=broadcast_notifications)
broadcast_thread.daemon = True
broadcast_thread.start()

while True:
    client_socket, addr = server_socket.accept()
    client_handler = threading.Thread(target=handle_client, args=(client_socket, addr))
    client_handler.start()
