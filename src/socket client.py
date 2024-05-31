import socket

def start_client():
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect(('localhost', 12346))

    try:
        # Receiving the notification message from the server
        notification_message = client_socket.recv(1024).decode('utf-8')
        print(f"Received notification: {notification_message}")
    except Exception as e:
        print(f"Error receiving notification: {e}")
    finally:
        client_socket.close()

if __name__ == "__main__":
    start_client()
