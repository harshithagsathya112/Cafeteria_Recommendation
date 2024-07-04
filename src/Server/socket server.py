import sys
import os
import socket
from Controller import ClientHandler

def main():
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    sys.path.append(project_root)
    
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(("0.0.0.0", 9999))
    server_socket.listen(5)
    print("Server listening on port 9999...")

    while True:
        client_socket, addr = server_socket.accept()
        print(f"Accepted connection from {addr}")
        handler = ClientHandler(client_socket)
        handler.handle_client()

if __name__ == "__main__":
    main()
