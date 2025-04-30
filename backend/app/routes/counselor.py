from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from ..services.counselor_service import get_counselor_profile

counselor_bp = Blueprint('counselor', __name__)

@counselor_bp.route('/api/counselors/<int:user_id>', methods=['GET'])
@jwt_required()
def get_counselor_details(user_id):
    current_user_id = get_jwt_identity()
    return get_counselor_profile(user_id, current_user_id)