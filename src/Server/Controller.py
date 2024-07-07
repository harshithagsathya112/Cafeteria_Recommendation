import sys
import os
import json
project_root =sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from Utils.Logger import log_activity
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(project_root)
from Models.Notification import Notification
from Models.UserLogin import User
from User_Services import User_Service
from Database.SQLConnect import DatabaseConnection

class ClientHandler:
    def __init__(self, client_socket):
        self.client_socket = client_socket
        self.notification = Notification()
        self.connection=DatabaseConnection().get_connection()
        self.user_service = User_Service(self.connection)

    def handle_client(self):
        while True:
            try:
                request = self.client_socket.recv(1024).decode('utf-8')
                if not request:
                    break
                print(f"Received request: {request}")
                response = self.process_request(request)
                self.client_socket.send(response.encode('utf-8'))
            except ConnectionResetError:
                break
            except Exception as e:
                print(f"Error: {e}")
                break
        self.client_socket.close()

    def process_request(self, request):
        request_parts = request.split(",")
        if request_parts[0] == "verify":
            return self.verify_user(request_parts[1], request_parts[2])
        else:
            return self.handle_role_based_request(request_parts)

    def verify_user(self, username, password):
        role_name, employee_id = User.verify_employee(username,password,self.connection)
        if role_name:
            notifications = Notification.get_unread_notifications(self.connection,employee_id)
            log_activity(f"User {username} with ID {employee_id} logged in as {role_name}")
            response = f"verified,{role_name},{employee_id},{json.dumps(notifications)}"
        else:
            response = "verification_failed"
        return response

    def handle_role_based_request(self, request_parts):
        role_name = request_parts[0]
        employee_id = int(request_parts[1])
        command = request_parts[2] if len(request_parts) > 2 else None
        args = request_parts[3:] if len(request_parts) > 3 else []

        if command:
            if role_name == 'Admin':
                if command == '5':
                    log_activity(f"User logged out of the system")
                response = self.user_service.execute_admin_command(command, args)
            elif role_name == 'Chef':
                response = self.user_service.execute_chef_command(command, employee_id, args)
            elif role_name == 'Employee':
                response = self.user_service.execute_user_command(command, employee_id, args)
            else:
                response = "Invalid role!"
            if response == "Logout":
                log_activity(f"User with ID {employee_id} logged out of the system")
        else:
            response = self.display_menu(role_name, employee_id)
        return response
