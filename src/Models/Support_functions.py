from Database.SQLConnect import execute_read_query

ADMIN_MENU = [
    "Admin Menu:",
    "1. Add Menu Item",
    "2. Update Menu Item",
    "3. Delete Menu Item",
    "4. View Menu",
    "5. Logout"
]

CHEF_MENU = [
    "Chef Menu:",
    "1. Roll Out Menu for Next Day",
    "2. Generate Monthly Feedback Report",
    "3. View Menu",
    "4. Send Final Menu for Today",
    "5. View Rollout menu",
    "6. View Recommendation",
    "7. View Discard menu List",
    "8. View reposnse for questions",
    "9. Logout"
]

EMPLOYEE_MENU = [
    "User Menu:",
    "1. View Menu",
    "2. Select Food Item",
    "3. Give Feedback",
    "4. View Rollout menu",
    "5. View Survey Questions",
    "6. Give Response for survey.",
    "7. Update Profile",
    "8. Logout"
]

def get_food_name(connection, food_item_id):
    query_fetch_food_item_name = f"SELECT ItemName FROM fooditem WHERE FoodItemID = {food_item_id}"
    food_item = execute_read_query(connection, query_fetch_food_item_name)
    return food_item[0][0] if food_item else None

def display_menu(role_name):
    if role_name == 'Admin':
        return "\n".join(ADMIN_MENU)
    elif role_name == 'Chef':
        return "\n".join(CHEF_MENU)
    elif role_name == 'Employee':
        return "\n".join(EMPLOYEE_MENU)
    else:
        raise ValueError("Invalid role name received from server.")
