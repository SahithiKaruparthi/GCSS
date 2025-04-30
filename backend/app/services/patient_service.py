from ..models.patient import Patient
from ..utils.db import get_db_connection
from flask import jsonify

def get_patients():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT p.id, p.first_name, p.last_name, p.date_of_birth, p.gender, 
               (SELECT risk_level FROM risk_reports WHERE patient_id = p.id ORDER BY assessment_date DESC LIMIT 1) as latest_risk
        FROM patients p
    """)
    patients = cursor.fetchall()
    conn.close()
    return jsonify(patients), 200

def get_patient(patient_id, current_user_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT role FROM users WHERE id = %s", (current_user_id,))
    user_role = cursor.fetchone()['role']
    
    if user_role == 'patient':
        cursor.execute("SELECT id FROM patients WHERE user_id = %s", (current_user_id,))
        patient = cursor.fetchone()
        if not patient or patient['id'] != patient_id:
            return jsonify({"msg": "Access denied"}), 403
    
    cursor.execute("SELECT * FROM patients WHERE id = %s", (patient_id,))
    patient = cursor.fetchone()
    conn.close()
    return jsonify(patient), 200