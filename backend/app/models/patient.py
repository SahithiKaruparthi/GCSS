from ..utils.db import get_db_connection

class Patient:
    @staticmethod
    def create_patient(user_id, first_name, last_name, date_of_birth, gender):
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO patients (user_id, first_name, last_name, date_of_birth, gender) VALUES (%s, %s, %s, %s, %s)",
            (user_id, first_name, last_name, date_of_birth, gender)
        )
        patient_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return patient_id

    @staticmethod
    def get_patient_by_user_id(user_id):
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM patients WHERE user_id = %s", (user_id,))
        patient = cursor.fetchone()
        conn.close()
        return patient