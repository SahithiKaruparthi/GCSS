from ..utils.db import get_db_connection

class FamilyHistory:
    @staticmethod
    def create_family_history(patient_id, relation, disease, onset_age, notes):
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO family_history (patient_id, relation, disease, onset_age, notes) VALUES (%s, %s, %s, %s, %s)",
            (patient_id, relation, disease, onset_age, notes)
        )
        history_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return history_id

    @staticmethod
    def get_family_history_by_patient_id(patient_id):
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM family_history WHERE patient_id = %s", (patient_id,))
        history = cursor.fetchall()
        conn.close()
        return history