import socket
import threading

def receive_notifications(client_socket):
    while True:
        try:
            notification = client_socket.recv(1024).decode()
            if notification:
                print(f"Notification received: {notification}")
        except:
            print("An error occurred. Closing connection.")
            client_socket.close()
            break

def send_messages(client_socket):
    while True:
        message = input("Enter message to send ('rollout_menu' to trigger notification): ")
        client_socket.send(message.encode())

def main():
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect(('localhost', 12345))

    receive_thread = threading.Thread(target=receive_notifications, args=(client_socket,))
    receive_thread.start()

    send_thread = threading.Thread(target=send_messages, args=(client_socket,))
    send_thread.start()

if __name__ == "__main__":
    main()
