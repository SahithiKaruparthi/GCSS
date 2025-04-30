from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from ..services.genetic_test_service import add_genetic_test

genetic_test_bp = Blueprint('genetic_test', __name__)

@genetic_test_bp.route('/api/patients/<int:patient_id>/genetic-tests', methods=['POST'])
@jwt_required()
def add_genetic_test_route(patient_id):
    data = request.get_json()
    current_user_id = get_jwt_identity()
    return add_genetic_test(patient_id, data, current_user_id)