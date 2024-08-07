import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from Database.SQLConnect import execute_read_query

class User:
    def __init__(self, name, employeeid):
        self.name = name
        self.employeeid = employeeid

    @staticmethod
    def get_role_from_employeeid(employeeid,connection):
        query = f"SELECT RoleName FROM role WHERE RoleID = (SELECT roleID FROM user WHERE EmployeeID = '{employeeid}')"
        get_role = execute_read_query(connection, query)
        if get_role:
            return get_role[0][0]  
        return None
    
    def login(self, role):
        if role == "Admin":
            return "Admin"
        elif role == "Chef":
            return 'Chef'
        else:
            return "Employee"

    @staticmethod
    def verify_employee(name, employeeid,connection):
        query_to_fetch_User = f"SELECT UserID FROM user WHERE name='{name}' AND EmployeeID='{employeeid}'"
        user = execute_read_query(connection, query_to_fetch_User )
        if user:
            user_instance = User(name, employeeid)
            role = user_instance.get_role_from_employeeid(employeeid,connection)
            if role:
                return user_instance.login(role), employeeid
        return None, None
    