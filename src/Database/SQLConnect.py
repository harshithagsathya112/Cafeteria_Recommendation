import mysql.connector
from mysql.connector import Error
import configparser
import os

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
        config_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'Data', 'config.ini'))
        config.read(config_path)

        db_config = {
            'host': config['mysql']['host'],
            'user': config['mysql']['user'],
            'password': config['mysql']['password'],
            'database': config['mysql']['database']
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

def main():
    db_connection = DatabaseConnection().get_connection()

    if db_connection is None:
        print("Failed to connect to the database")
        return

    create_table_query = """
    CREATE TABLE IF NOT EXISTS user (
        UserID INT AUTO_INCREMENT PRIMARY KEY,
        name VARCHAR(100),
        EmployeeID VARCHAR(100),
        roleID INT
    );
    """
    execute_query(db_connection, create_table_query)
    print("User table created successfully.")

    insert_data_query = """
    INSERT INTO user (name, EmployeeID, roleID) VALUES
    ('John Doe', '123456', 1),
    ('Jane Smith', '654321', 2);
    """
    execute_query(db_connection, insert_data_query)
    print("Data inserted successfully.")

    select_query = "SELECT * FROM user"
    results = execute_read_query(db_connection, select_query)

    for row in results:
        print(row)

if __name__ == '__main__':
    main()
