from ..models.genetic_test import GeneticTest
from ..utils.db import get_db_connection
from flask import jsonify

def add_genetic_test(patient_id, data, current_user_id):
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM counselors WHERE user_id = %s", (current_user_id,))
        counselor = cursor.fetchone()
        if not counselor:
            return jsonify({"msg": "Counselor not found"}), 404

        test_id = GeneticTest.create_genetic_test(
            patient_id,
            data.get('test_date'),
            data.get('gene'),
            data.get('mutation'),
            data.get('result'),
            data.get('risk_level'),
            counselor['id']
        )
        conn.commit()

        # Trigger risk report creation
        cursor.execute("CALL CalculateRisk(%s, @risk_level, @risk_score)", (patient_id,))
        cursor.execute("SELECT @risk_level as risk_level, @risk_score as risk_score")
        risk = cursor.fetchone()

        return jsonify({"msg": "Genetic test added successfully", "risk": risk}), 201
    except Exception as e:
        conn.rollback()
        return jsonify({"msg": f"Error: {str(e)}"}), 500
    finally:
        conn.close()