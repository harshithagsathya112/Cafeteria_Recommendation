import socket
import threading
import sys
import os
import json
from Logger import log_activity
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), 'Class')))
from Cafeteria import Cafeteria
from SQLConnect import create_connection, execute_read_query,execute_query
from UserLogin import User


def get_notifications(employee_id):
    connection = create_connection()
    query = f"SELECT Message FROM notification WHERE UserID = (SELECT UserID FROM user WHERE EmployeeID = '{employee_id}') AND IsRead = 0"
    notifications = execute_read_query(connection, query)
    if notifications:
        update_query = f"UPDATE notification SET IsRead = 1 WHERE UserID = (SELECT UserID FROM user WHERE EmployeeID = '{employee_id}') AND IsRead = 0"
        execute_query(connection, update_query)
    return [notification[0] for notification in notifications]



def handle_client(client_socket, Cafetertia_system):
    while True:
        try:
            request = client_socket.recv(1024).decode('utf-8')
            if not request:
                break
            print(f"Received request: {request}")
            request_parts = request.split(",")
            if request_parts[0] == "verify":
                role_name, employee_id = User.verify_employee(request_parts[1], request_parts[2])
                if role_name:
                    notifications = get_notifications(employee_id)
                    log_activity(f"User {request_parts[1]} with ID {request_parts[2]} logged in as {role_name}")
                    response = f"verified,{role_name},{employee_id},{json.dumps(notifications)}"
                else:
                    response = "verification_failed"
                client_socket.send(response.encode('utf-8'))
                continue

            role_name = request_parts[0]
            employee_id = int(request_parts[1])
            command = request_parts[2] if len(request_parts) > 2 else None
            args = request_parts[3:] if len(request_parts) > 3 else []

            if command:
                if role_name == 'Admin':
                    if command==5:
                        log_activity(f"User logged out of the system")
                    response = Cafetertia_system.execute_admin_command(command, args)   
                elif role_name == 'Chef':
                    response = Cafetertia_system.execute_chef_command(command, args)
                elif role_name == 'Employee':
                    response = Cafetertia_system.execute_user_command(command, employee_id, args)
                else:
                    response = "Invalid role!"
                if response == "Exit":
                    log_activity(f"User with ID {employee_id} logged out of the system")
                    client_socket.send(response.encode('utf-8'))
                    break
            else:
                if role_name == 'Admin':
                    menu_generator = Cafetertia_system.admin_menu()
                elif role_name == 'Chef':
                    menu_generator = Cafetertia_system.chef_menu()
                elif role_name == 'Employee':
                    menu_generator = Cafetertia_system.user_menu(employee_id)
                else:
                    response = "Invalid role!"
                    client_socket.send(response.encode('utf-8'))
                    continue
                response = next(menu_generator)
            client_socket.send(response.encode('utf-8'))
        except ConnectionResetError:
            break
        except Exception as e:
            print(f"Error: {e}")
            break
    client_socket.close()

def main():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)  
    server.bind(("0.0.0.0", 9999))
    server.listen(5)
    print("Server listening on port 9999")
    connection = create_connection()
    Cafetertia_system =Cafeteria(connection)
    while True:
        client_socket, addr = server.accept()
        print(f"Accepted connection from {addr}")
        client_handler = threading.Thread(target=handle_client, args=(client_socket, Cafetertia_system))
        client_handler.start()

if __name__ == "__main__":
    main()