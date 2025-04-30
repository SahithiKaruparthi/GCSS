from ..models.lifestyle_factor import LifestyleFactor
from ..utils.db import get_db_connection
from flask import jsonify

def add_lifestyle_factor(patient_id, data, current_user_id):
    conn = get_db_connection()
    try:
        factor_id = LifestyleFactor.create_lifestyle_factor(
            patient_id,
            data.get('factor_type'),
            data.get('value'),
            data.get('notes')
        )
        conn.commit()

        # Trigger risk report creation
        cursor = conn.cursor()
        cursor.execute("CALL CalculateRisk(%s, @risk_level, @risk_score)", (patient_id,))
        cursor.execute("SELECT @risk_level as risk_level, @risk_score as risk_score")
        risk = cursor.fetchone()

        return jsonify({"msg": "Lifestyle factor added successfully", "risk": risk}), 201
    except Exception as e:
        conn.rollback()
        return jsonify({"msg": f"Error: {str(e)}"}), 500
    finally:
        conn.close()