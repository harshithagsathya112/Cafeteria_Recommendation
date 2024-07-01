import socket
import json,sys,os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), 'Class')))
from Support_functions import display_menu

def handle_input_request(prompt):
    response = input(prompt)
    return response

def process_command(role_name, command):
    args = []
    if role_name == 'Admin' and command in ['1', '2', '3']:
        if command == '1':
            args.append(handle_input_request("Enter food name: "))
            args.append(handle_input_request("Enter food price: "))
        elif command == '2':
            args.append(handle_input_request("Enter food id: "))
            args.append(handle_input_request("Enter food name: "))
            args.append(handle_input_request("Enter food price: "))
        elif command == '3':
            args.append(handle_input_request("Enter food id: "))
    elif role_name == 'Employee' and command in ['2', '3','5','6']:
        if command == '2':
            args.append(handle_input_request("Enter food item ID to select: "))
        elif command == '3':
            args.append(handle_input_request("Enter food item ID: "))
            args.append(handle_input_request("Enter your comment: "))
            args.append(handle_input_request("Enter your rating (1-5): "))
        elif command == '5':
            pass
        elif command == '6':
            args.append(handle_input_request("Enter question ID: "))
            args.append(handle_input_request("Enter your response: "))

    elif role_name == 'Chef' and command in ['1', '5','7','8','Remove','Feedback']:
        if command == '1':
            args.append(handle_input_request("Enter the meal type (e.g., breakfast, lunch, dinner): "))
            args.append(handle_input_request("Enter the food item ID: "))
        elif command == '5':
            args.append(handle_input_request("Enter the meal type (e.g., breakfast, lunch, dinner): "))
            args.append(handle_input_request("Enter the food item ID: "))
        elif command == '7':
            args.append(handle_input_request("No of items you want to view from recommendation engine: "))
        elif command=='8':
            FlagDiscardoption=True
        elif (command=='Feedback' or 'Remove'):
            args.append(handle_input_request("Enter the food item ID: "))



    return args

def main():
    while True:
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client.connect(("127.0.0.1", 9999))
        user_name = input("Enter your name: ")
        employee_id = input("Enter your employee ID: ")

        verification_request = f"verify,{user_name},{employee_id}" 
        client.send(verification_request.encode('utf-8'))
        response = client.recv(1024).decode('utf-8')

        if response.startswith("verified"):
            _, role_name, verified_employee_id, notifications = response.split(',', 3)
            notifications = json.loads(notifications)
            if notifications:
                print("Notifications:")
                for notification in notifications:
                    print(f"- {notification}")
        else:
            print("Verification failed. Exiting.")
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
            elif role_name == 'Employee' and command == '7':
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