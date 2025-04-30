from ..models.risk_report import RiskReport
from ..utils.db import get_db_connection
from flask import jsonify
from datetime import datetime

def get_risk_assessment(patient_id, current_user_id):
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT role FROM users WHERE id = %s", (current_user_id,))
        user_role = cursor.fetchone()['role']

        if user_role == 'patient':
            cursor.execute("SELECT id FROM patients WHERE user_id = %s", (current_user_id,))
            patient = cursor.fetchone()
            if not patient or patient['id'] != patient_id:
                return jsonify({"msg": "Access denied"}), 403

        cursor.execute("SELECT * FROM risk_reports WHERE patient_id = %s ORDER BY assessment_date DESC LIMIT 1", (patient_id,))
        risk_report = cursor.fetchone()

        if not risk_report:
            cursor.execute("CALL CalculateRisk(%s, @risk_level, @risk_score)", (patient_id,))
            cursor.execute("SELECT @risk_level as risk_level, @risk_score as risk_score")
            risk = cursor.fetchone()
            return jsonify({
                "risk_level": risk['risk_level'],
                "risk_score": risk['risk_score'],
                "assessment_date": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                "recommendations": "Automated calculation (no formal report)"
            }), 200

        return jsonify(risk_report), 200
    finally:
        conn.close()