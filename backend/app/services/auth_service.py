from ..utils.db import get_db_connection
from ..models.user import User
from werkzeug.security import generate_password_hash, check_password_hash
from flask_jwt_extended import create_access_token
from flask import jsonify

def register_user(data):
    email = data.get('email')
    password = data.get('password')
    role = data.get('role', 'patient')
    
    if not email or not password:
        return jsonify({"msg": "Email and password are required"}), 400
    
    hashed_password = generate_password_hash(password)
    
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM users WHERE email = %s", (email,))
        if cursor.fetchone():
            return jsonify({"msg": "User already exists"}), 409
        
        cursor.execute(
            "INSERT INTO users (email, password, role) VALUES (%s, %s, %s)",
            (email, hashed_password, role)
        )
        user_id = cursor.lastrowid
        
        if role == 'patient':
            cursor.execute(
                "INSERT INTO patients (user_id, first_name, last_name, date_of_birth, gender) VALUES (%s, %s, %s, %s, %s)",
                (user_id, data.get('first_name'), data.get('last_name'), data.get('date_of_birth'), data.get('gender'))
            )
        elif role == 'counselor':
            cursor.execute(
                "INSERT INTO counselors (user_id, first_name, last_name, certification_number, specialty) VALUES (%s, %s, %s, %s, %s)",
                (user_id, data.get('first_name'), data.get('last_name'), data.get('certification_number'), data.get('specialty'))
            )
        
        conn.commit()
        return jsonify({"msg": "User registered successfully", "id": user_id}), 201
    except Exception as e:
        conn.rollback()
        return jsonify({"msg": f"Error: {str(e)}"}), 500
    finally:
        conn.close()

def login_user(data):
    email = data.get('email')
    password = data.get('password')
    
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT id, email, password, role FROM users WHERE email = %s", (email,))
        user = cursor.fetchone()
        
        if not user or not check_password_hash(user['password'], password):
            return jsonify({"msg": "Invalid credentials"}), 401
        
        access_token = create_access_token(identity=user['id'])
        
        if user['role'] == 'patient':
            cursor.execute("SELECT id, first_name, last_name FROM patients WHERE user_id = %s", (user['id'],))
            details = cursor.fetchone()
        elif user['role'] == 'counselor':
            cursor.execute("SELECT id, first_name, last_name, specialty FROM counselors WHERE user_id = %s", (user['id'],))
            details = cursor.fetchone()
        else:
            details = {}
        
        return jsonify({
            "access_token": access_token,
            "user_id": user['id'],
            "role": user['role'],
            "details": details
        }), 200
    finally:
        conn.close()