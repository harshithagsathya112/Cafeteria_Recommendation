import socket
import json,sys,os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from Client.Command_processing import process_command
from Models.Support_functions import display_menu
from Utils.Input_Validation import *

def main():
    Max_Attempts=3
    Attempts_count=0
    
    while Attempts_count<Max_Attempts:
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client.connect(("127.0.0.1", 9999))
        user_name = input("Enter your name: ")
        employee_id = input("Enter your employee ID: ")

        verification_request = f"verify,{user_name},{employee_id}" 
        client.send(verification_request.encode('utf-8'))
        response = client.recv(1024).decode('utf-8')

        if response.startswith("verified"):
            _, role_name, verified_employee_id, notifications = response.split(',', 3)
            Attempts_count=0
            notifications = json.loads(notifications)
            if notifications:
                print("Notifications:")
                for notification in notifications:
                    print(f"- {notification}")
        else:
            print("Verification failed.")
            Attempts_count+=1
            if(Attempts_count==Max_Attempts):
                print("YOUR MAX ATTEMPTS HAVE OVER !!!")
            should_exit = True
            client.close()
            continue

        should_exit = False

        while not should_exit:
            menu_display = display_menu(role_name)
            print(menu_display)

            command = input("Enter your Choice: ")
            if role_name == 'Admin' and command == '5':
                should_exit = True
            elif role_name == 'Chef' and command == '10':
                should_exit = True
            elif role_name == 'Employee' and command == '8':
                should_exit = True

            args = process_command(role_name, command)
            
            request = f"{role_name},{verified_employee_id},{command},{','.join(args)}"
            client.send(request.encode('utf-8'))
            response = client.recv(1024).decode('utf-8')
            print(f"Received response:\n{response}")

            if should_exit:
                break
        client.close()

    client.close()

if __name__ == "__main__":
    main()