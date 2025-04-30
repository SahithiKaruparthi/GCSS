from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from ..services.patient_service import get_patients, get_patient

patient_bp = Blueprint('patient', __name__)

@patient_bp.route('/api/patients', methods=['GET'])
@jwt_required()
def get_all_patients():
    return get_patients()

@patient_bp.route('/api/patients/<int:patient_id>', methods=['GET'])
@jwt_required()
def get_patient_details(patient_id):
    current_user_id = get_jwt_identity()
    return get_patient(patient_id, current_user_id)