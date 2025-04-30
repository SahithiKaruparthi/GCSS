from ..utils.db import get_db_connection

class Counselor:
    @staticmethod
    def create_counselor(user_id, first_name, last_name, certification_number, specialty):
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO counselors (user_id, first_name, last_name, certification_number, specialty) VALUES (%s, %s, %s, %s, %s)",
            (user_id, first_name, last_name, certification_number, specialty)
        )
        counselor_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return counselor_id

    @staticmethod
    def get_counselor_by_user_id(user_id):
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM counselors WHERE user_id = %s", (user_id,))
        counselor = cursor.fetchone()
        conn.close()
        return counselor