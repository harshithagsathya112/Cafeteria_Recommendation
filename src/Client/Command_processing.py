from Client.Input_Validation import validate_input, update_profile_input
def process_command(role_name, command):
    args = []
    if role_name == 'Admin' and command in ['1', '2', '3']:
        if command == '1':
            args.append(validate_input("Enter food name: "))
            args.append(validate_input("Enter food price: "))
        elif command == '2':
            args.append(validate_input("Enter food id: "))
            args.append(validate_input("Enter food name: "))
            args.append(validate_input("Enter food price: "))
        elif command == '3':
            args.append(validate_input("Enter food id: "))

    elif role_name == 'Employee' and command in ['2', '3','5','6','7']:
        if command == '2':
            args.append(validate_input("Enter food item ID to select: "))
        elif command == '3':
            args.append(validate_input("Enter food item ID: "))
            args.append(validate_input("Enter your comment: "))
            args.append(validate_input("Enter your rating (1-5): "))
        elif command == '5':
            pass
        elif command == '6':
            args.append(validate_input("Enter question ID: "))
            args.append(validate_input("Enter your response: "))
        elif command == '7':
            args=update_profile_input()
            args = [str(arg) for arg in args]

    elif role_name == 'Chef' and command in ['1', '5','7','8','Remove','Feedback']:
        if command == '1':
            args.append(validate_input("Enter the meal type (e.g., breakfast, lunch, dinner): "))
            args.append(validate_input("Enter the food item ID: "))
        elif command == '5':
            args.append(validate_input("Enter the meal type (e.g., breakfast, lunch, dinner): "))
            args.append(validate_input("Enter the food item ID: "))
        elif command == '7':
            args.append(validate_input("No of items you want to view from recommendation engine: "))
        elif (command=='Feedback' or 'Remove'):
            args.append(validate_input("Enter the food item ID: "))
    return args