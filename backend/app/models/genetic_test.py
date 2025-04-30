from ..utils.db import get_db_connection

class GeneticTest:
    @staticmethod
    def create_genetic_test(patient_id, test_date, gene, mutation, result, risk_level, counselor_id):
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO genetic_tests (patient_id, test_date, gene, mutation, result, risk_level, counselor_id) VALUES (%s, %s, %s, %s, %s, %s, %s)",
            (patient_id, test_date, gene, mutation, result, risk_level, counselor_id)
        )
        test_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return test_id

    @staticmethod
    def get_genetic_tests_by_patient_id(patient_id):
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM genetic_tests WHERE patient_id = %s", (patient_id,))
        tests = cursor.fetchall()
        conn.close()
        return tests