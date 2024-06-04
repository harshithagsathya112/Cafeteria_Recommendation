from flask import Flask, request, jsonify, session
from functools import wraps

app = Flask(__name__)
app.secret_key = 'super-secret-key'  # Change this to a secure key in production

# Dummy user database
users = {
    'admin': {'password': 'adminpass', 'role': 'admin'},
    'chef': {'password': 'chefpass', 'role': 'chef'},
    'employee': {'employee_id': '123', 'name': 'John Doe', 'role': 'employee'}
}

@app.route('/login', methods=['POST'])
def login():
    username = request.json.get('username')
    password = request.json.get('password')
    user = users.get(username)

    if user and user.get('password') == password:
        session['username'] = username
        session['role'] = user['role']
        return jsonify({'msg': 'Login successful'}), 200

    return jsonify({'msg': 'Bad username or password'}), 401

@app.route('/login_employee', methods=['POST'])
def login_employee():
    employee_id = request.json.get('employee_id')
    name = request.json.get('name')
    user = users.get('employee')

    if user and user.get('employee_id') == employee_id and user.get('name') == name:
        session['employee_id'] = employee_id
        session['role'] = user['role']
        return jsonify({'msg': 'Login successful'}), 200

    return jsonify({'msg': 'Invalid employee ID or name'}), 401

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'role' not in session:
            return jsonify({'msg': 'Please log in first'}), 401
        return f(*args, **kwargs)
    return decorated_function

def role_required(role):
    def wrapper(fn):
        @wraps(fn)
        def decorated_view(*args, **kwargs):
            if 'role' not in session:
                return jsonify({'msg': 'Please log in first'}), 401
            if session['role'] != role:
                return jsonify({'msg': 'Access denied'}), 403
            return fn(*args, **kwargs)
        return decorated_view
    return wrapper

# Admin only endpoint
@app.route('/api/admin', methods=['GET'])
@role_required('admin')
def admin_endpoint():
    return jsonify({'msg': 'Welcome admin'}), 200

# Chef only endpoint
@app.route('/api/chef', methods=['GET'])
@role_required('chef')
def chef_endpoint():
    return jsonify({'msg': 'Welcome chef'}), 200

# Employee only endpoint (no token required)
@app.route('/api/employee', methods=['GET'])
@login_required
def employee_endpoint():
    if session['role'] != 'employee':
        return jsonify({'msg': 'Access denied'}), 403

    return jsonify({'msg': 'Welcome employee'}), 200

if __name__ == '__main__':
    app.run(debug=True)
