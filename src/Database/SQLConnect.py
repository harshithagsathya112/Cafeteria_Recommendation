import mysql.connector
from mysql.connector import Error
import configparser
import os

CONFIG_FILE_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'Data', 'config.ini'))
MYSQL_SECTION = 'mysql'
HOST_KEY = 'host'
USER_KEY = 'user'
PASSWORD_KEY = 'password'
DATABASE_KEY = 'database'

class DatabaseConnection:
    instance = None

    def __new__(cls):
        if cls.instance is None:
            cls.instance = super(DatabaseConnection, cls).__new__(cls)
            cls.instance.connection = None
            cls.instance.create_connection()
        return cls.instance

    def create_connection(self):
        config = configparser.ConfigParser()
        config.read(CONFIG_FILE_PATH)

        db_config = {
            'host': config[MYSQL_SECTION][HOST_KEY],
            'user': config[MYSQL_SECTION][USER_KEY],
            'password': config[MYSQL_SECTION][PASSWORD_KEY],
            'database': config[MYSQL_SECTION][DATABASE_KEY]
        }

        try:
            self.connection = mysql.connector.connect(**db_config)
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
