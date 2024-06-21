from SQLConnect import connection, execute_read_query

def get_food_name(food_item_id):
        query = f"SELECT ItemName FROM fooditem WHERE FoodItemID = {food_item_id}"
        result = execute_read_query(connection, query)
        return result[0][0] 