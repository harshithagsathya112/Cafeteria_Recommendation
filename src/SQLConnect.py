import mysql.connector
from mysql.connector import Error

def execute_read_query(connection, query):
    cursor = connection.cursor()
    result = None
    try:
        cursor.execute(query)
        result = cursor.fetchall()
        return result
    except Error as e:
        print(f"The error '{e}' occurred")

def create_connection(host_name, user_name, user_password, db_name):
    connection = None
    try:
        connection = mysql.connector.connect(
            host=host_name,
            user=user_name,
            passwd=user_password,
            database=db_name
        )
        print("Connection to MySQL DB successful")
        #select_users = "SELECT RoleName FROM cafeteria.role WHERE RoleID = 1;"
        '''select_users = "SELECT * FROM cafeteria.role "
        users = execute_read_query(connection, select_users)

        for user in users:
            print(f"'{user[1]}' is the role " )'''
        
    except Error as e:
        print(f"The error '{e}' occurred")

    return connection
if __name__ == "__main__":
# Replace the parameters with your MySQL server details
    connection = create_connection("localhost", "root", "Harshitha@555", "cafeteria")