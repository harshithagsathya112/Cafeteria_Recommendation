import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from SQLConnect import create_connection, execute_read_query

class User:
    def __init__(self, name, employeeid):
        self.name = name
        self.employeeid = employeeid

    def get_role_from_employeeid(self):
        connection = create_connection()
        query = f"SELECT RoleName FROM role WHERE RoleID = (SELECT roleID FROM user WHERE EmployeeID = '{self.employeeid}')"
        get_role = execute_read_query(connection, query)
        if get_role:
            return get_role[0][0]  # Accessing the first element of the first tuple
        return None

    def login(self, role):
        if role == "Admin":
            print("Welcome, Admin!")
            return "Admin"
        elif role == "Chef":
            print("Welcome, Chef!")
            return 'Chef'
        else:
            print("Welcome, Employee!")
            return "Employee"

    @staticmethod
    def userinput():
        name = input("Enter your name: ")
        employeeid = input("Enter employee ID: ")
        return name, employeeid

    @staticmethod
    def verify_employee(name, employeeid):
        connection = create_connection()
        query = f"SELECT UserID FROM user WHERE name='{name}' AND EmployeeID='{employeeid}'"
        user = execute_read_query(connection, query)
        return user != []
    
def run():
    name, employeeid = User.userinput()
    user = User(name, employeeid)
    if User.verify_employee(name, employeeid):
        role = user.get_role_from_employeeid()
        if role:
            return user.login(role),employeeid
        else:
            print("Role not found.")
    else:
        print("User not verified.")

if __name__ == "__main__":
    '''name, employeeid = User.userinput()
    user = User(name, employeeid)
    if User.verify_employee(name, employeeid):
        role = user.get_role_from_employeeid()
        if role:
            user.login(role)
        else:
            print("Role not found.")
    else:
        print("User not verified.")'''
    run()
