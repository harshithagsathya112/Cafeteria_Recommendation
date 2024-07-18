import os
import sys
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(project_root)
from Database.SQLConnect import execute_read_query

ADMIN_ROLE = "Admin"
CHEF_ROLE = "Chef"
DEFAULT_ROLE = "Employee"

class User:
    def __init__(self, name, employee_id):
        self.name = name
        self.employee_id = employee_id

    @staticmethod
    def get_role_from_employee_id(employee_id, connection):
        query = f"SELECT RoleName FROM role WHERE RoleID = (SELECT RoleID FROM user WHERE EmployeeID = '{employee_id}')"
        role_result = execute_read_query(connection, query)
        if role_result:
            return role_result[0][0]
        return None
    
    def login(self, role):
        if role == ADMIN_ROLE:
            return ADMIN_ROLE
        elif role == CHEF_ROLE:
            return CHEF_ROLE
        else:
            return DEFAULT_ROLE

    @staticmethod
    def verify_employee(name, employee_id, connection):
        query = f"SELECT UserID FROM user WHERE name = '{name}' AND EmployeeID = '{employee_id}'"
        user_result = execute_read_query(connection, query)
        
        if user_result:
            user_instance = User(name, employee_id)
            role = user_instance.get_role_from_employee_id(employee_id, connection)
            if role:
                return user_instance.login(role), employee_id
        
        return None, None
