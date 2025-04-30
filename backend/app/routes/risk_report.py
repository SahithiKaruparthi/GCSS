from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from ..services.risk_report_service import get_risk_assessment

risk_report_bp = Blueprint('risk_report', __name__)

@risk_report_bp.route('/api/patients/<int:patient_id>/risk', methods=['GET'])
@jwt_required()
def get_risk_assessment_route(patient_id):
    current_user_id = get_jwt_identity()
    return get_risk_assessment(patient_id, current_user_id)