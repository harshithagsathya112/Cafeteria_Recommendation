import socket
import json
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from Client.Command_processing import process_command
from Models.Support_functions import display_menu
from Utils.Input_Validation import *

MAX_ATTEMPTS = 3
SERVER_ADDRESS = "127.0.0.1"
SERVER_PORT = 9999
COMMAND_EXIT_ADMIN = '5'
COMMAND_EXIT_CHEF = '9'
COMMAND_EXIT_EMPLOYEE = '8'
ROLE_ADMIN = 'Admin'
ROLE_CHEF = 'Chef'
ROLE_EMPLOYEE = 'Employee'

def main():

    attempts_count = 0
    
    while attempts_count < MAX_ATTEMPTS:
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client.connect((SERVER_ADDRESS, SERVER_PORT))
        
        user_name = input("Enter your name: ")
        employee_id = input("Enter your employee ID: ")

        verification_request = f"verify,{user_name},{employee_id}" 
        client.send(verification_request.encode('utf-8'))
        response = client.recv(1024).decode('utf-8')

        if response.startswith("verified"):
            _, role_name, verified_employee_id, notifications = response.split(',', 3)
            attempts_count = 0
            notifications = json.loads(notifications)
            if notifications:
                print("Notifications:")
                for notification in notifications:
                    print(f"- {notification}")
        else:
            print("Verification failed.")
            attempts_count += 1
            if attempts_count == MAX_ATTEMPTS:
                print("YOUR MAX ATTEMPTS HAVE OVER !!!")
            client.close()
            continue

        should_exit = False

        while not should_exit:
            menu_display = display_menu(role_name)
            print(menu_display)

            command = input("Enter your Choice: ")
            if (role_name == ROLE_ADMIN and command == COMMAND_EXIT_ADMIN) or \
               (role_name == ROLE_CHEF and command == COMMAND_EXIT_CHEF) or \
               (role_name == ROLE_EMPLOYEE and command == COMMAND_EXIT_EMPLOYEE):
                should_exit = True

            args = process_command(role_name, command)
            
            request = f"{role_name},{verified_employee_id},{command},{','.join(args)}"
            client.send(request.encode('utf-8'))
            response = client.recv(1024).decode('utf-8')
            print(f"Received response:\n{response}")

            if should_exit:
                break

        client.close()

if __name__ == "__main__":
    main()
