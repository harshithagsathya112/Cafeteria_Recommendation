import sys
import os
import json
from Logger import log_activity
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), 'Class')))
from Notification import get_notifications
from UserLogin import User

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
