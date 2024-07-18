from Utils.Input_Validation import *

ADMIN_COMMANDS = {
    '1': 'Add Menu Item',
    '2': 'Update Menu Item',
    '3': 'Delete Menu Item'
}

EMPLOYEE_COMMANDS = {
    '2': 'Select Food Item',
    '3': 'Give Feedback',
    '5': 'View Rollout menu',
    '6': 'Give Response for survey',
    '7': 'Update Profile'
}

CHEF_COMMANDS = {
    '1': 'Roll Out Menu for Next Day',
    '4': 'Send Final Menu for Today',
    '6': 'View Recommendation',
    'Remove': 'Remove',
    'Feedback': 'Feedback'
}

PROMPT_FOOD_NAME = "Enter food name: "
PROMPT_FOOD_PRICE = "Enter food price: "
PROMPT_FOOD_ID = "Enter food id: "
PROMPT_COMMENT = "Enter your comment: "
PROMPT_RATING = "Enter your rating (1-5): "
PROMPT_QUESTION_ID = "Enter question ID: "
PROMPT_RESPONSE = "Enter your response: "
PROMPT_MEAL_TYPE = "Enter the meal type (e.g., breakfast, lunch, dinner): "
PROMPT_NUM_ITEMS = "No of items you want to view from recommendation engine: "
PROMPT_FOOD_ITEM_ID = "Enter the food item ID: "
MEAL_TYPE_OPTIONS = ['breakfast', 'lunch', 'dinner']
RATING_OPTIONS = [1, 2, 3, 4, 5]

def process_command(role_name, command):
    args = []

    if role_name == 'Admin' and command in ADMIN_COMMANDS:
        if command == '1':
            args.append(handle_input_request(PROMPT_FOOD_NAME))
            args.append(handle_input_request(PROMPT_FOOD_PRICE))
        elif command == '2':
            args.append(handle_input_request(PROMPT_FOOD_ID))
            args.append(handle_input_request(PROMPT_FOOD_NAME))
            args.append(handle_input_request(PROMPT_FOOD_PRICE))
        elif command == '3':
            args.append(handle_input_request(PROMPT_FOOD_ID))

    elif role_name == 'Employee' and command in EMPLOYEE_COMMANDS:
        if command == '2':
            args.append(handle_input_request(PROMPT_FOOD_ITEM_ID))
        elif command == '3':
            args.append(handle_input_request(PROMPT_FOOD_ITEM_ID))
            args.append(handle_input_request(PROMPT_COMMENT))
            args.append(validate_input(PROMPT_RATING, RATING_OPTIONS))
        elif command == '6':
            args.append(handle_input_request(PROMPT_QUESTION_ID))
            args.append(handle_input_request(PROMPT_RESPONSE))
        elif command == '7':
            args = update_profile_input()
            args = [str(arg) for arg in args]

    elif role_name == 'Chef' and command in CHEF_COMMANDS:
        if command in {'1', '4'}:
            args.append(validate_input(PROMPT_MEAL_TYPE, MEAL_TYPE_OPTIONS))
            args.append(handle_input_request(PROMPT_FOOD_ITEM_ID))
        elif command == '6':
            args.append(handle_input_request(PROMPT_NUM_ITEMS))
        elif command in {'Feedback', 'Remove'}:
            args.append(handle_input_request(PROMPT_FOOD_ITEM_ID))

    return args
