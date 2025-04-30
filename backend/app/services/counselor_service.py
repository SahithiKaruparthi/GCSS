from ..models.counselor import Counselor
from ..utils.db import get_db_connection
from flask import jsonify

def get_counselor_profile(user_id, current_user_id):
    if current_user_id != user_id:
        return jsonify({"msg": "Access denied"}), 403

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM counselors WHERE user_id = %s", (user_id,))
    counselor = cursor.fetchone()
    conn.close()
    return jsonify(counselor), 200