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

def create_connection():
    connection = None
    try:
        connection = mysql.connector.connect(
        host="localhost",
        user="root",
        password= "Harshitha@555",
        database="cafeteria"
    )
        
    except Error as e:
        print(f"The error '{e}' occurred")

    return connection


if __name__ == "__main__":
# Replace the parameters with your MySQL server details
    connection = create_connection("localhost", "root", "Harshitha@555", "cafeteria")