from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required
from ..services.stats_service import get_risk_distribution, get_gene_mutation_counts, get_disease_distribution

stats_bp = Blueprint('stats', __name__)

@stats_bp.route('/api/stats/risk-distribution', methods=['GET'])
@jwt_required()
def get_risk_distribution_route():
    return get_risk_distribution()

@stats_bp.route('/api/stats/gene-mutation-counts', methods=['GET'])
@jwt_required()
def get_gene_mutation_counts_route():
    return get_gene_mutation_counts()

@stats_bp.route('/api/stats/disease-distribution', methods=['GET'])
@jwt_required()
def get_disease_distribution_route():
    return get_disease_distribution()