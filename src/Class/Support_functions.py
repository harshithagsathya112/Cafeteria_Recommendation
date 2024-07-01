from SQLConnect import connection, execute_read_query

def get_food_name(food_item_id):
        query = f"SELECT ItemName FROM fooditem WHERE FoodItemID = {food_item_id}"
        result = execute_read_query(connection, query)
        return result[0][0] 

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
            "9. View reposnse for quqestions",
            "10. Logout"
        ]
    elif role_name == 'Employee':
        menu = [
            "User Menu:",
            "1. View Menu",
            "2. Select Food Item",
            "3. Give Feedback",
            "4. View Rollout menu",
            "5. View Survey Questions",
            "6. Give Response for survey.",
            "7. Logout"
        ]
    else:
        raise ValueError("Invalid role name received from server.")
    
    return "\n".join(menu)