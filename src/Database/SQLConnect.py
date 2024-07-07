import mysql.connector
from mysql.connector import Error

class DatabaseConnection:
    instance = None

    def __new__(cls):
        if cls.instance is None:
            cls.instance = super(DatabaseConnection, cls).__new__(cls)
            cls.instance.connection = None
            cls.instance.create_connection()
        return cls.instance

    def create_connection(self):
        try:
            self.connection = mysql.connector.connect(
                host="localhost",
                user="root",
                password="Harshitha@555",
                database="cafeteriadb"
            )
        except Error as e:
            print(f"The error '{e}' occurred")

    def get_connection(self):
        return self.connection
    
def execute_read_query(connection, query):
    cursor = connection.cursor()
    result = None
    try:
        cursor.execute(query)
        result = cursor.fetchall()
        return result
    except Error as e:
        print(f"The error '{e}' occurred")
   
def execute_query(connection, query):
    cursor = connection.cursor()
    try:
        cursor.execute(query)
        connection.commit()
    except Error as e:
        print(f"The error '{e}' occurred")
