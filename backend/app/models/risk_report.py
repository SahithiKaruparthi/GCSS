from ..utils.db import get_db_connection

class RiskReport:
    @staticmethod
    def create_risk_report(patient_id, counselor_id, risk_level, risk_score, recommendations):
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO risk_reports (patient_id, counselor_id, risk_level, risk_score, recommendations) VALUES (%s, %s, %s, %s, %s)",
            (patient_id, counselor_id, risk_level, risk_score, recommendations)
        )
        report_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return report_id

    @staticmethod
    def get_risk_reports_by_patient_id(patient_id):
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM risk_reports WHERE patient_id = %s ORDER BY assessment_date DESC", (patient_id,))
        reports = cursor.fetchall()
        conn.close()
        return reports