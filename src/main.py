import socket
import threading
import sys
import os
# Add the Class directory to the system path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), 'Class')))
from Cafeteria import MenuSystem
from SQLConnect import create_connection
def handle_client(client_socket, menu_system):
    while True:
        try:
            # Receive a request from the client
            request = client_socket.recv(1024).decode('utf-8')
            if not request:
                break
            print(f"Received request: {request}")
            # Process the request
            request_parts = request.split(",")
            role_name = request_parts[0]
            employee_id = int(request_parts[1])
            command = request_parts[2] if len(request_parts) > 2 else None
            args = request_parts[3:] if len(request_parts) > 3 else []
            
            if command:
                if role_name == 'Admin':
                    response = menu_system.execute_admin_command(command, args)
                elif role_name == 'Chef':
                    response = menu_system.execute_chef_command(command, args)
                elif role_name == 'Employee':
                    response = menu_system.execute_user_command(command, employee_id, args)
                else:
                    response = "Invalid role!"
                if response == "Exit":
                    client_socket.send(response.encode('utf-8'))
                    break
            else:
                if role_name == 'Admin':
                    menu_generator = menu_system.admin_menu()
                elif role_name == 'Chef':
                    menu_generator = menu_system.chef_menu()
                elif role_name == 'Employee':
                    menu_generator = menu_system.user_menu(employee_id)
                else:
                    response = "Invalid role!"
                    client_socket.send(response.encode('utf-8'))
                    continue
                response = next(menu_generator)
            # Send a response back to the client
            client_socket.send(response.encode('utf-8'))
        except ConnectionResetError:
            break
        except Exception as e:
            print(f"Error: {e}")
            break
    client_socket.close()
def main():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(("0.0.0.0", 9999))
    server.listen(5)
    print("Server listening on port 9999")
    # Create a database connection
    connection = create_connection()
    menu_system = MenuSystem(connection)
    while True:
        client_socket, addr = server.accept()
        print(f"Accepted connection from {addr}")
        client_handler = threading.Thread(target=handle_client, args=(client_socket, menu_system))
        client_handler.start()
if __name__ == "__main__":
    main()
