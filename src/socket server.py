import socket
import threading
import sys
import os
import json

# Add the Class directory to the system path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), 'Class')))
from Cafeteria import MenuSystem
from SQLConnect import create_connection, execute_read_query,execute_query

class User:
    def __init__(self, name, employeeid):
        self.name = name
        self.employeeid = employeeid

    def get_role_from_employeeid(self):
        connection = create_connection()
        query = f"SELECT RoleName FROM role WHERE RoleID = (SELECT roleID FROM user WHERE EmployeeID = '{self.employeeid}')"
        get_role = execute_read_query(connection, query)
        if get_role:
            return get_role[0][0]  # Accessing the first element of the first tuple
        return None

    def login(self, role):
        if role == "Admin":
            return "Admin"
        elif role == "Chef":
            return 'Chef'
        else:
            return "Employee"

    @staticmethod
    def verify_employee(name, employeeid):
        connection = create_connection()
        query = f"SELECT UserID FROM user WHERE name='{name}' AND EmployeeID='{employeeid}'"
        user = execute_read_query(connection, query)
        if user:
            user_instance = User(name, employeeid)
            role = user_instance.get_role_from_employeeid()
            if role:
                return user_instance.login(role), employeeid
        return None, None

def get_notifications(employee_id):
    connection = create_connection()
    query = f"SELECT Message FROM notification WHERE UserID = (SELECT UserID FROM user WHERE EmployeeID = '{employee_id}') AND IsRead = 0"
    notifications = execute_read_query(connection, query)
    if notifications:
        update_query = f"UPDATE notification SET IsRead = 1 WHERE UserID = (SELECT UserID FROM user WHERE EmployeeID = '{employee_id}') AND IsRead = 0"
        execute_query(connection, update_query)
    return [notification[0] for notification in notifications]

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
            if request_parts[0] == "verify":
                role_name, employee_id = User.verify_employee(request_parts[1], request_parts[2])
                if role_name:
                    notifications = get_notifications(employee_id)
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
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)  # Reuse the address
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
