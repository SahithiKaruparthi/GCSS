from flask import Flask, request, jsonify
from dotenv import load_dotenv
from flask_cors import CORS
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from werkzeug.security import generate_password_hash, check_password_hash
import pymysql
import os
from datetime import datetime, timedelta
import json
from functools import wraps
from flask_mail import Mail, Message

app = Flask(__name__)

# Configuration
app.config['JWT_SECRET_KEY'] = os.environ.get('JWT_SECRET_KEY', 'dev-secret-key')
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=1)
app.config['MYSQL_HOST'] = os.environ.get('MYSQL_HOST', 'localhost')
app.config['MYSQL_USER'] = os.environ.get('MYSQL_USER', 'root')
app.config['MYSQL_PASSWORD'] = os.environ.get('MYSQL_PASSWORD', 'password')
app.config['MYSQL_DB'] = os.environ.get('MYSQL_DB', 'genetic_counseling')
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = os.environ.get('MAIL_USERNAME')
app.config['MAIL_PASSWORD'] = os.environ.get('MAIL_PASSWORD')

# Initialize extensions
jwt = JWTManager(app)
mail = Mail(app)
CORS(app)

# Database connection
def get_db_connection():
    return pymysql.connect(
        host=app.config['MYSQL_HOST'],
        user=app.config['MYSQL_USER'],
        password=app.config['MYSQL_PASSWORD'],
        db=app.config['MYSQL_DB'],
        cursorclass=pymysql.cursors.DictCursor
    )

# Role-based access control
def role_required(roles):
    def decorator(fn):
        @wraps(fn)
        @jwt_required()
        def wrapper(*args, **kwargs):
            current_user_id = get_jwt_identity()
            conn = get_db_connection()
            try:
                cursor = conn.cursor()
                cursor.execute("SELECT role FROM users WHERE id = %s", (current_user_id,))
                user = cursor.fetchone()
                if user['role'] not in roles:
                    return jsonify({"msg": "Access denied"}), 403
                return fn(*args, **kwargs)
            finally:
                conn.close()
        return wrapper
    return decorator

# Authentication routes
@app.route('/api/register', methods=['POST'])
def register():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')
    role = data.get('role', 'patient')
    
    # Validate inputs
    if not email or not password:
        return jsonify({"msg": "Email and password are required"}), 400
    
    # Hash password
    hashed_password = generate_password_hash(password)
    
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        
        # Check if user already exists
        cursor.execute("SELECT id FROM users WHERE email = %s", (email,))
        if cursor.fetchone():
            return jsonify({"msg": "User already exists"}), 409
        
        # Insert user
        cursor.execute(
            "INSERT INTO users (email, password, role) VALUES (%s, %s, %s)",
            (email, hashed_password, role)
        )
        user_id = cursor.lastrowid
        
        # Insert patient or counselor details
        if role == 'patient':
            cursor.execute(
                "INSERT INTO patients (user_id, first_name, last_name, date_of_birth, gender) VALUES (%s, %s, %s, %s, %s)",
                (user_id, data.get('first_name'), data.get('last_name'), data.get('date_of_birth'), data.get('gender'))
            )
        elif role == 'counselor':
            cursor.execute(
                "INSERT INTO counselors (user_id, first_name, last_name, certification_number, specialty) VALUES (%s, %s, %s, %s, %s)",
                (user_id, data.get('first_name'), data.get('last_name'), data.get('certification_number'), data.get('specialty'))
            )
        
        conn.commit()
        return jsonify({"msg": "User registered successfully", "id": user_id}), 201
    except Exception as e:
        conn.rollback()
        return jsonify({"msg": f"Error: {str(e)}"}), 500
    finally:
        conn.close()

@app.route('/api/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')
    
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT id, email, password, role FROM users WHERE email = %s", (email,))
        user = cursor.fetchone()
        
        if not user or not check_password_hash(user['password'], password):
            return jsonify({"msg": "Invalid credentials"}), 401
        
        # Create access token
        access_token = create_access_token(identity=user['id'])
        
        # Get additional user details
        if user['role'] == 'patient':
            cursor.execute("SELECT id, first_name, last_name FROM patients WHERE user_id = %s", (user['id'],))
            details = cursor.fetchone()
        elif user['role'] == 'counselor':
            cursor.execute("SELECT id, first_name, last_name, specialty FROM counselors WHERE user_id = %s", (user['id'],))
            details = cursor.fetchone()
        else:
            details = {}
        
        return jsonify({
            "access_token": access_token,
            "user_id": user['id'],
            "role": user['role'],
            "details": details
        }), 200
    finally:
        conn.close()

# Patient routes
@app.route('/api/patients', methods=['GET'])
@role_required(['counselor', 'admin'])
def get_patients():
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT p.id, p.first_name, p.last_name, p.date_of_birth, p.gender, 
                   (SELECT risk_level FROM risk_reports WHERE patient_id = p.id ORDER BY assessment_date DESC LIMIT 1) as latest_risk
            FROM patients p
        """)
        patients = cursor.fetchall()
        return jsonify(patients), 200
    finally:
        conn.close()

@app.route('/api/patients/<int:patient_id>', methods=['GET'])
@role_required(['patient', 'counselor', 'admin'])
def get_patient(patient_id):
    current_user_id = get_jwt_identity()
    
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        
        # Check if current user is the patient or has counselor/admin role
        cursor.execute("SELECT role FROM users WHERE id = %s", (current_user_id,))
        user_role = cursor.fetchone()['role']
        
        if user_role == 'patient':
            cursor.execute("SELECT id FROM patients WHERE user_id = %s", (current_user_id,))
            patient = cursor.fetchone()
            if not patient or patient['id'] != patient_id:
                return jsonify({"msg": "Access denied"}), 403
        
        # Get patient details
        cursor.execute("""
            SELECT p.id, p.first_name, p.last_name, p.date_of_birth, p.gender
            FROM patients p
            WHERE p.id = %s
        """, (patient_id,))
        patient = cursor.fetchone()
        
        if not patient:
            return jsonify({"msg": "Patient not found"}), 404
        
        # Get lifestyle factors
        cursor.execute("""
            SELECT factor_type, value, notes
            FROM lifestyle_factors
            WHERE patient_id = %s
        """, (patient_id,))
        lifestyle_factors = cursor.fetchall()
        
        # Get genetic tests
        cursor.execute("""
            SELECT id, test_date, gene, mutation, result, risk_level
            FROM genetic_tests
            WHERE patient_id = %s
        """, (patient_id,))
        genetic_tests = cursor.fetchall()
        
        # Get family history
        cursor.execute("""
            SELECT id, relation, disease, onset_age, notes
            FROM family_history
            WHERE patient_id = %s
        """, (patient_id,))
        family_history = cursor.fetchall()
        
        # Get risk reports
        cursor.execute("""
            SELECT r.id, r.assessment_date, r.risk_level, r.risk_score, r.recommendations,
                   c.first_name as counselor_first_name, c.last_name as counselor_last_name
            FROM risk_reports r
            JOIN counselors c ON r.counselor_id = c.id
            WHERE r.patient_id = %s
            ORDER BY r.assessment_date DESC
        """, (patient_id,))
        risk_reports = cursor.fetchall()
        
        return jsonify({
            "patient": patient,
            "lifestyle_factors": lifestyle_factors,
            "genetic_tests": genetic_tests,
            "family_history": family_history,
            "risk_reports": risk_reports
        }), 200
    finally:
        conn.close()

# Genetic test routes
@app.route('/api/patients/<int:patient_id>/genetic-tests', methods=['POST'])
@role_required(['counselor', 'admin'])
def add_genetic_test(patient_id):
    data = request.get_json()
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        
        # Get counselor ID
        current_user_id = get_jwt_identity()
        cursor.execute("SELECT id FROM counselors WHERE user_id = %s", (current_user_id,))
        counselor = cursor.fetchone()
        if not counselor:
            return jsonify({"msg": "Counselor not found"}), 404
        
        # Insert genetic test
        cursor.execute("""
            INSERT INTO genetic_tests (patient_id, test_date, gene, mutation, result, risk_level, counselor_id)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, (
            patient_id,
            data.get('test_date'),
            data.get('gene'),
            data.get('mutation'),
            data.get('result'),
            data.get('risk_level'),
            counselor['id']
        ))
        
        conn.commit()
        
        # Trigger will automatically create a new risk report
        
        # Get latest risk report
        cursor.execute("""
            SELECT risk_level, risk_score
            FROM risk_reports
            WHERE patient_id = %s
            ORDER BY assessment_date DESC
            LIMIT 1
        """, (patient_id,))
        risk_report = cursor.fetchone()
        
        # Send notification if high risk
        if risk_report and risk_report['risk_level'] == 'High':
            cursor.execute("""
                SELECT p.first_name, p.last_name, u.email
                FROM patients p
                JOIN users u ON p.user_id = u.id
                WHERE p.id = %s
            """, (patient_id,))
            patient = cursor.fetchone()
            
            if patient and app.config['MAIL_USERNAME']:
                msg = Message(
                    subject="High Risk Assessment Alert",
                    sender=app.config['MAIL_USERNAME'],
                    recipients=[patient['email']]
                )
                msg.body = f"Dear {patient['first_name']},\n\nA new genetic test has been added to your profile, and your risk level has been assessed as HIGH. Please contact your genetic counselor for more information.\n\nRegards,\nGenetic Counseling Support System"
                mail.send(msg)
        
        return jsonify({"msg": "Genetic test added successfully", "risk_report": risk_report}), 201
    except Exception as e:
        conn.rollback()
        return jsonify({"msg": f"Error: {str(e)}"}), 500
    finally:
        conn.close()

# Family history routes
@app.route('/api/patients/<int:patient_id>/family-history', methods=['POST'])
@role_required(['counselor', 'admin', 'patient'])
def add_family_history(patient_id):
    data = request.get_json()
    
    # Verify access for patient role
    current_user_id = get_jwt_identity()
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT role FROM users WHERE id = %s", (current_user_id,))
        user_role = cursor.fetchone()['role']
        
        if user_role == 'patient':
            cursor.execute("SELECT id FROM patients WHERE user_id = %s", (current_user_id,))
            patient = cursor.fetchone()
            if not patient or patient['id'] != patient_id:
                return jsonify({"msg": "Access denied"}), 403
        
        # Insert family history
        cursor.execute("""
            INSERT INTO family_history (patient_id, relation, disease, onset_age, notes)
            VALUES (%s, %s, %s, %s, %s)
        """, (
            patient_id,
            data.get('relation'),
            data.get('disease'),
            data.get('onset_age'),
            data.get('notes')
        ))
        
        conn.commit()
        
        # Manual risk calculation - could be improved with a trigger
        cursor.execute("CALL CalculateRisk(%s, @risk_level, @risk_score)", (patient_id,))
        cursor.execute("SELECT @risk_level as risk_level, @risk_score as risk_score")
        risk = cursor.fetchone()
        
        # Get counselor ID (use first available if patient is adding)
        if user_role == 'patient':
            cursor.execute("SELECT id FROM counselors ORDER BY id LIMIT 1")
            counselor = cursor.fetchone()
            counselor_id = counselor['id'] if counselor else 1
        else:
            cursor.execute("SELECT id FROM counselors WHERE user_id = %s", (current_user_id,))
            counselor = cursor.fetchone()
            counselor_id = counselor['id'] if counselor else 1
        
        # Insert risk report
        cursor.execute("""
            INSERT INTO risk_reports (patient_id, counselor_id, risk_level, risk_score, recommendations)
            VALUES (%s, %s, %s, %s, %s)
        """, (
            patient_id,
            counselor_id,
            risk['risk_level'],
            risk['risk_score'],
            f"Automatic risk assessment based on new family history entry: {data.get('relation')} with {data.get('disease')}"
        ))
        
        conn.commit()
        
        return jsonify({"msg": "Family history added successfully", "risk": risk}), 201
    except Exception as e:
        conn.rollback()
        return jsonify({"msg": f"Error: {str(e)}"}), 500
    finally:
        conn.close()

# Lifestyle factors routes
@app.route('/api/patients/<int:patient_id>/lifestyle-factors', methods=['POST'])
@role_required(['counselor', 'admin', 'patient'])
def add_lifestyle_factor(patient_id):
    data = request.get_json()
    
    # Verify access for patient role
    current_user_id = get_jwt_identity()
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT role FROM users WHERE id = %s", (current_user_id,))
        user_role = cursor.fetchone()['role']
        
        if user_role == 'patient':
            cursor.execute("SELECT id FROM patients WHERE user_id = %s", (current_user_id,))
            patient = cursor.fetchone()
            if not patient or patient['id'] != patient_id:
                return jsonify({"msg": "Access denied"}), 403
        
        # Insert lifestyle factor
        cursor.execute("""
            INSERT INTO lifestyle_factors (patient_id, factor_type, value, notes)
            VALUES (%s, %s, %s, %s)
        """, (
            patient_id,
            data.get('factor_type'),
            data.get('value'),
            data.get('notes')
        ))
        
        conn.commit()
        
        # Manual risk calculation
        cursor.execute("CALL CalculateRisk(%s, @risk_level, @risk_score)", (patient_id,))
        cursor.execute("SELECT @risk_level as risk_level, @risk_score as risk_score")
        risk = cursor.fetchone()
        
        # Get counselor ID (use first available if patient is adding)
        if user_role == 'patient':
            cursor.execute("SELECT id FROM counselors ORDER BY id LIMIT 1")
            counselor = cursor.fetchone()
            counselor_id = counselor['id'] if counselor else 1
        else:
            cursor.execute("SELECT id FROM counselors WHERE user_id = %s", (current_user_id,))
            counselor = cursor.fetchone()
            counselor_id = counselor['id'] if counselor else 1
        
        # Insert risk report
        cursor.execute("""
            INSERT INTO risk_reports (patient_id, counselor_id, risk_level, risk_score, recommendations)
            VALUES (%s, %s, %s, %s, %s)
        """, (
            patient_id,
            counselor_id,
            risk['risk_level'],
            risk['risk_score'],
            f"Automatic risk assessment based on new lifestyle factor: {data.get('factor_type')}"
        ))
        
        conn.commit()
        
        return jsonify({"msg": "Lifestyle factor added successfully", "risk": risk}), 201
    except Exception as e:
        conn.rollback()
        return jsonify({"msg": f"Error: {str(e)}"}), 500
    finally:
        conn.close()

# Risk assessment routes
@app.route('/api/patients/<int:patient_id>/risk', methods=['GET'])
@role_required(['counselor', 'admin', 'patient'])
def get_risk_assessment(patient_id):
    # Verify access for patient role
    current_user_id = get_jwt_identity()
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT role FROM users WHERE id = %s", (current_user_id,))
        user_role = cursor.fetchone()['role']
        
        if user_role == 'patient':
            cursor.execute("SELECT id FROM patients WHERE user_id = %s", (current_user_id,))
            patient = cursor.fetchone()
            if not patient or patient['id'] != patient_id:
                return jsonify({"msg": "Access denied"}), 403
        
        # Get latest risk report
        cursor.execute("""
            SELECT r.id, r.assessment_date, r.risk_level, r.risk_score, r.recommendations,
                   c.first_name as counselor_first_name, c.last_name as counselor_last_name
            FROM risk_reports r
            JOIN counselors c ON r.counselor_id = c.id
            WHERE r.patient_id = %s
            ORDER BY r.assessment_date DESC
            LIMIT 1
        """, (patient_id,))
        
        risk_report = cursor.fetchone()
        
        if not risk_report:
            # Calculate risk if no report exists
            cursor.execute("CALL CalculateRisk(%s, @risk_level, @risk_score)", (patient_id,))
            cursor.execute("SELECT @risk_level as risk_level, @risk_score as risk_score")
            risk = cursor.fetchone()
            
            return jsonify({
                "risk_level": risk['risk_level'],
                "risk_score": risk['risk_score'],
                "assessment_date": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                "recommendations": "Automated calculation (no formal report)"
            }), 200
        
        return jsonify(risk_report), 200
    finally:
        conn.close()

# Risk statistics for dashboard
@app.route('/api/stats/risk-distribution', methods=['GET'])
@role_required(['counselor', 'admin'])
def get_risk_distribution():
    conn = get_db_connection()
    try:
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
        
        return jsonify(distribution), 200
    finally:
        conn.close()

@app.route('/api/stats/gene-mutation-counts', methods=['GET'])
@role_required(['counselor', 'admin'])
def get_gene_mutation_counts():
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT gene, COUNT(*) as count
            FROM genetic_tests
            GROUP BY gene
            ORDER BY count DESC
            LIMIT 10
        """)
        gene_counts = cursor.fetchall()
        
        return jsonify(gene_counts), 200
    finally:
        conn.close()

@app.route('/api/stats/disease-distribution', methods=['GET'])
@role_required(['counselor', 'admin'])
def get_disease_distribution():
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT disease, COUNT(*) as count
            FROM family_history
            GROUP BY disease
            ORDER BY count DESC
            LIMIT 10
        """)
        disease_counts = cursor.fetchall()
        
        return jsonify(disease_counts), 200
    finally:
        conn.close()

# Generate PDF report
from flask import send_file
import io
from reportlab.pdfgen import canvas

@app.route('/api/patients/<int:patient_id>/generate-report', methods=['GET'])
@role_required(['counselor', 'admin', 'patient'])
def generate_report(patient_id):
    # Fetch patient data
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT role FROM users WHERE id = %s", (get_jwt_identity(),))
        user_role = cursor.fetchone()['role']
        
        if user_role == 'patient':
            cursor.execute("SELECT id FROM patients WHERE user_id = %s", (get_jwt_identity(),))
            patient = cursor.fetchone()
            if not patient or patient['id'] != patient_id:
                return jsonify({"msg": "Access denied"}), 403
        
        # Get patient details
        cursor.execute("""
            SELECT p.id, p.first_name, p.last_name, p.date_of_birth, p.gender
            FROM patients p
            WHERE p.id = %s
        """, (patient_id,))
        patient = cursor.fetchone()
        
        if not patient:
            return jsonify({"msg": "Patient not found"}), 404
        
        # Get latest risk report
        cursor.execute("""
            SELECT r.id, r.assessment_date, r.risk_level, r.risk_score, r.recommendations,
                   c.first_name as counselor_first_name, c.last_name as counselor_last_name
            FROM risk_reports r
            JOIN counselors c ON r.counselor_id = c.id
            WHERE r.patient_id = %s
            ORDER BY r.assessment_date DESC
            LIMIT 1
        """, (patient_id,))
        risk_report = cursor.fetchone()
        
        # Create a PDF report
        buffer = io.BytesIO()
        p = canvas.Canvas(buffer)
        p.drawString(100, 750, f"Patient Report: {patient['first_name']} {patient['last_name']}")
        p.drawString(100, 730, f"Date of Birth: {patient['date_of_birth']}")
        p.drawString(100, 710, f"Gender: {patient['gender']}")
        p.showPage()
        p.save()
        
        # Return the PDF as a downloadable file
        buffer.seek(0)
        return send_file(buffer, as_attachment=True, download_name='patient_report.pdf', mimetype='application/pdf')
    finally:
        conn.close()

@app.route('/api/<string:role>s/<int:user_id>', methods=['GET'])
@jwt_required()
def get_profile(role, user_id):
    current_user_id = get_jwt_identity()

    # Verify access
    if current_user_id != user_id:
        return jsonify({"msg": "Access denied"}), 403

    conn = get_db_connection()
    try:
        cursor = conn.cursor()

        if role == 'patient':
            cursor.execute("""
                SELECT p.id, p.first_name, p.last_name, p.date_of_birth, p.gender
                FROM patients p
                WHERE p.user_id = %s
            """, (user_id,))
        elif role == 'counselor':
            cursor.execute("""
                SELECT c.id, c.first_name, c.last_name, c.certification_number, c.specialty
                FROM counselors c
                WHERE c.user_id = %s
            """, (user_id,))
        else:
            return jsonify({"msg": "Invalid role"}), 400

        profile = cursor.fetchone()
        if not profile:
            return jsonify({"msg": "Profile not found"}), 404

        return jsonify(profile), 200
    finally:
        conn.close()

# Run the application
if __name__ == '__main__':
    app.run(debug=True)