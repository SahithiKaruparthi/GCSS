from ..utils.db import get_db_connection
from flask import jsonify

def get_risk_distribution():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT risk_level, COUNT(*) as count
        FROM (
            SELECT patient_id, risk_level,
                   ROW_NUMBER() OVER (PARTITION BY patient_id ORDER BY assessment_date DESC) as rn
            FROM risk_reports
        ) as latest_reports
        WHERE rn = 1
        GROUP BY risk_level
    """)
    distribution = cursor.fetchall()
    conn.close()
    return jsonify(distribution), 200

def get_gene_mutation_counts():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT gene, COUNT(*) as count
        FROM genetic_tests
        GROUP BY gene
        ORDER BY count DESC
        LIMIT 10
    """)
    gene_counts = cursor.fetchall()
    conn.close()
    return jsonify(gene_counts), 200

def get_disease_distribution():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT disease, COUNT(*) as count
        FROM family_history
        GROUP BY disease
        ORDER BY count DESC
        LIMIT 10
    """)
    disease_counts = cursor.fetchall()
    conn.close()
    return jsonify(disease_counts), 200