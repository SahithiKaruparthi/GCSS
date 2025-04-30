from ..models.family_history import FamilyHistory
from ..utils.db import get_db_connection
from flask import jsonify

def add_family_history(patient_id, data, current_user_id):
    conn = get_db_connection()
    try:
        history_id = FamilyHistory.create_family_history(
            patient_id,
            data.get('relation'),
            data.get('disease'),
            data.get('onset_age'),
            data.get('notes')
        )
        conn.commit()

        # Trigger risk report creation
        cursor = conn.cursor()
        cursor.execute("CALL CalculateRisk(%s, @risk_level, @risk_score)", (patient_id,))
        cursor.execute("SELECT @risk_level as risk_level, @risk_score as risk_score")
        risk = cursor.fetchone()

        return jsonify({"msg": "Family history added successfully", "risk": risk}), 201
    except Exception as e:
        conn.rollback()
        return jsonify({"msg": f"Error: {str(e)}"}), 500
    finally:
        conn.close()