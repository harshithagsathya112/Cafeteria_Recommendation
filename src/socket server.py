import socket
import threading

def handle_client(client_socket):
    try:
        # Sending a notification message to the client
        notification_message = "Hello! This is a notification from the server."
        client_socket.sendall(notification_message.encode('utf-8'))
    except Exception as e:
        print(f"Error handling client: {e}")
    finally:
        client_socket.close()

def start_server():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)  # Reuse the socket
    server_socket.bind(('localhost', 12346))
    server_socket.listen(5)  # Listen for up to 5 connections
    print("Server is listening on port 12345")

    while True:
        client_socket, addr = server_socket.accept()
        print(f"Accepted connection from {addr}")
        client_handler = threading.Thread(target=handle_client, args=(client_socket,))
        client_handler.start()

if __name__ == "__main__":
    start_server()
