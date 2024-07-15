from Utils.Input_Validation import *

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

    elif role_name == 'Employee' and command in ['2', '3','5','6','7']:
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
        elif command == '7':
            args=update_profile_input()
            args = [str(arg) for arg in args]

    elif role_name == 'Chef' and command in ['1', '5','7','Remove','Feedback']:
        if command == '1':
            args.append(validate_input("Enter the meal type (e.g., breakfast, lunch, dinner): ",['breakfast', 'lunch', 'dinner']))
            args.append(handle_input_request("Enter the food item ID: "))
        elif command == '5':
            args.append(validate_input("Enter the meal type (e.g., breakfast, lunch, dinner): ",['breakfast', 'lunch', 'dinner']))
            args.append(handle_input_request("Enter the food item ID: "))
        elif command == '7':
            args.append(handle_input_request("No of items you want to view from recommendation engine: "))
        elif (command=='Feedback' or 'Remove'):
            args.append(handle_input_request("Enter the food item ID: "))
    return args