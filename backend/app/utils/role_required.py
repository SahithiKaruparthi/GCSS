from functools import wraps
from flask_jwt_extended import get_jwt_identity
from ..utils.db import get_db_connection
from flask import jsonify

def role_required(roles):
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            current_user_id = get_jwt_identity()
            conn = get_db_connection()
            try:
                cursor = conn.cursor()
                cursor.execute("SELECT role FROM users WHERE id = %s", (current_user_id,))
                user = cursor.fetchone()
                if user['role'] not in roles:
                    return jsonify({"msg": "Access denied"}), 403
                return fn(*args, **kwargs)
            finally:
                conn.close()
        return wrapper
    return decorator