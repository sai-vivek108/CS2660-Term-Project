from flask import request, jsonify, render_template
from google.cloud import firestore
from app.qr_utils import generate_qr_code
from app.models import add_session, record_attendance
from google.cloud import storage
from datetime import datetime

BUCKET_NAME = "qr-attendance-bucket"

db = firestore.Client()  # Initialize Firestore client

# helper function
def get_session_details():
    
    current_date = datetime.now().strftime('%Y-%m-%d')
    session_id = f"session-{current_date}"
    course_name = "CS1660"
    return current_date, session_id, course_name

def setup_routes(app):
    @app.route('/')
    def home():
        return render_template('home.html')

    @app.route('/generate', methods=['POST'])
    def generate():
        current_date, session_id, course_name = get_session_details()

        if not session_id or not course_name or not current_date:
            return jsonify({"error": "Missing required fields"}), 400
        
        # Add session to Firestore
        ### Commented bc firestone isn't set up yet
        add_session(session_id, course_name, current_date)
        
        # Generate QR code
        response, status = generate_qr_code(session_id)
        return jsonify({"message": response}), status

    @app.route('/attendance/form/<session_id>', methods=['GET'])
    def attendance_form(session_id):
        return render_template('attendance_form.html', current_date=session_id.split("session-")[1])

    @app.route('/qrCode', methods=['GET'])
    def display_qrCode():
        try:
            current_date, session_id, _ = get_session_details()
            qr_url = f"https://storage.googleapis.com/qr-attendance-bucket-griffin/{session_id}.png"
            
            return render_template('qrCode.html', qr_url=qr_url, session_id=session_id, current_date=current_date)
        
        except Exception as e:
            return jsonify({"error": str(e)}), 500

    @app.route('/submit_attendance', methods=['POST'])
    def submit_attendance():
        try:
            # Get form data
            session_id = request.form.get('session_id')
            student_id = request.form.get('student_id')
            present = True  # Since student scanned the QR
    
            if not session_id or not student_id:
                return jsonify({"error": "Session ID and Student ID are required"}), 400
    
            # Record the attendance 
            response, status_code = record_attendance(session_id, student_id, present)
    
            return jsonify(response), status_code
    
        except Exception as e:
            return jsonify({"error": str(e)}), 500

    @app.route('/attendance/<session_id>', methods=['GET'])
    def get_attendance(session_id):
        """
        Fetch attendance records for a specific session.
        """
        try:
            attendance_ref = db.collection('Sessions').document(f"Session_{session_id}").collection('Attendance')
            
            # Query all attendance records in the subcollection
            attendance_docs = attendance_ref.stream()

            # Compile attendance data into a list
            attendance_records = []
            for doc in attendance_docs:
                record = doc.to_dict()
                attendance_records.append(record)

            return jsonify({
                "session_id": session_id,
                "attendance_records": attendance_records
            }), 200

        except Exception as e:
            return jsonify({"error": str(e)}), 500
