from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from ..services.family_history_service import add_family_history

family_history_bp = Blueprint('family_history', __name__)

@family_history_bp.route('/api/patients/<int:patient_id>/family-history', methods=['POST'])
@jwt_required()
def add_family_history_route(patient_id):
    data = request.get_json()
    current_user_id = get_jwt_identity()
    return add_family_history(patient_id, data, current_user_id)