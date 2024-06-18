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
        database="cafeteriadb"
    )
        
    except Error as e:
        print(f"The error '{e}' occurred")

    return connection
   
def execute_query(connection, query):
    cursor = connection.cursor()
    try:
        cursor.execute(query)
        connection.commit()
    except Error as e:
        print(f"The error '{e}' occurred")


#if __name__ == "__main__":
# Replace the parameters with your MySQL server details
connection = create_connection()