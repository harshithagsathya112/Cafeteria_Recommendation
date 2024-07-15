import unittest
from unittest.mock import patch, MagicMock
from mysql.connector import Error
import configparser
import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from Database.SQLConnect import DatabaseConnection, execute_query, execute_read_query 

class TestDatabaseFunctions(unittest.TestCase):

    @patch('Database.SQLConnect.mysql.connector.connect')
    @patch('Database.SQLConnect.configparser.ConfigParser.read')
    def test_database_connection(self, mock_config_read, mock_mysql_connect):
        mock_mysql_connect.return_value = MagicMock()
        mock_config_read.return_value = True

        db_instance = DatabaseConnection()
        connection = db_instance.get_connection()
        self.assertIsNotNone(connection)
        self.assertTrue(mock_mysql_connect.called)
    
    @patch('Database.SQLConnect.DatabaseConnection.get_connection')
    def test_execute_query(self, mock_get_connection):
        mock_connection = MagicMock()
        mock_cursor = mock_connection.cursor.return_value
        mock_get_connection.return_value = mock_connection

        query = "CREATE TABLE test (id INT);"
        execute_query(mock_connection, query)
        
        mock_cursor.execute.assert_called_once_with(query)
        mock_connection.commit.assert_called_once()

    @patch('Database.SQLConnect.DatabaseConnection.get_connection')
    def test_execute_read_query(self, mock_get_connection):
        mock_connection = MagicMock()
        mock_cursor = mock_connection.cursor.return_value
        mock_cursor.fetchall.return_value = [('John Doe', '123456', 1)]
        mock_get_connection.return_value = mock_connection

        query = "SELECT * FROM test;"
        results = execute_read_query(mock_connection, query)
        
        mock_cursor.execute.assert_called_once_with(query)
        self.assertEqual(results, [('John Doe', '123456', 1)])
    
    

if __name__ == '__main__':
    unittest.main()
