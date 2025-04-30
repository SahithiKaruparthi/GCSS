from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from ..services.lifestyle_factor_service import add_lifestyle_factor

lifestyle_factor_bp = Blueprint('lifestyle_factor', __name__)

@lifestyle_factor_bp.route('/api/patients/<int:patient_id>/lifestyle-factors', methods=['POST'])
@jwt_required()
def add_lifestyle_factor_route(patient_id):
    data = request.get_json()
    current_user_id = get_jwt_identity()
    return add_lifestyle_factor(patient_id, data, current_user_id)