from ..utils.db import get_db_connection

class LifestyleFactor:
    @staticmethod
    def create_lifestyle_factor(patient_id, factor_type, value, notes):
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO lifestyle_factors (patient_id, factor_type, value, notes) VALUES (%s, %s, %s, %s)",
            (patient_id, factor_type, value, notes)
        )
        factor_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return factor_id

    @staticmethod
    def get_lifestyle_factors_by_patient_id(patient_id):
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM lifestyle_factors WHERE patient_id = %s", (patient_id,))
        factors = cursor.fetchall()
        conn.close()
        return factors