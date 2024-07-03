import socket
import threading
import sys
import os
from ClientHandler import handle_client
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from Server.Controller import Controller
from SQLConnect import create_connection

def main():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)  
    server.bind(("0.0.0.0", 9999))
    server.listen(10)
    print("Server listening on port 9999")
    connection = create_connection()
    Cafetertia_system =Controller(connection)
    while True:
        client_socket, addr = server.accept()
        print(f"Accepted connection from {addr}")
        client_handler = threading.Thread(target=handle_client, args=(client_socket, Cafetertia_system))
        client_handler.start()

if __name__ == "__main__":
    main()