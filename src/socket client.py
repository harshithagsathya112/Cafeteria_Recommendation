import socket
import json

def handle_input_request(prompt):
    response = input(prompt)
    return response

def display_menu(role_name):
    menu = []
    if role_name == 'Admin':
        menu = [
            "Admin Menu:",
            "1. Add Menu Item",
            "2. Update Menu Item",
            "3. Delete Menu Item",
            "4. View Menu",
            "5. Logout"
        ]
    elif role_name == 'Chef':
        menu = [
            "Chef Menu:",
            "1. Roll Out Menu for Next Day",
            "2. View Feedback",
            "3. Generate Monthly Feedback Report",
            "4. View Menu",
            "5. Send Final Menu for Today",
            "6. View Rollout menu",
            "7. View Recommendation",
            "8. View Discard menu List",
            "9. Logout"
        ]
    elif role_name == 'Employee':
        menu = [
            "User Menu:",
            "1. View Menu",
            "2. Select Food Item",
            "3. Give Feedback",
            "4. View Rollout menu",
            "5. Logout"
        ]
    else:
        raise ValueError("Invalid role name received from server.")
    
    return "\n".join(menu)

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
    elif role_name == 'Employee' and command in ['2', '3']:
        if command == '2':
            args.append(handle_input_request("Enter food item ID to select: "))
        elif command == '3':
            args.append(handle_input_request("Enter food item ID: "))
            args.append(handle_input_request("Enter your comment: "))
            args.append(handle_input_request("Enter your rating (1-5): "))
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
            elif role_name == 'Chef' and command == '9':
                should_exit = True
            elif role_name == 'Employee' and command == '5':
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