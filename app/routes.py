from flask import request, jsonify, render_template
from google.cloud import firestore
from app.qr_utils import generate_qr_code
from app.models import add_session

db = firestore.Client()  # Initialize Firestore client

def setup_routes(app):
    
    @app.route('/')
    def home():
        return render_template('home.html')


    @app.route('/generate', methods=['POST'])
    def generate():
        data = request.json
        session_id = data.get('session_id')
        course_name = data.get('course_name')
        date = data.get('date')
        
        if not session_id or not course_name or not date:
            return jsonify({"error": "Missing required fields"}), 400
        
        # Add session to Firestore
        add_session(session_id, course_name, date)
        
        # Generate QR code
        response, status = generate_qr_code(session_id)
        return jsonify({"message": response}), status
    
    @app.route('/attendance/form/<session_id>', methods=['GET'])
    def attendance_form(session_id):
        return render_template('attendance_form.html', session_id=session_id)

    @app.route('/submit_attendance', methods=['POST'])
    def submit_attendance():
        try:
            # Get form data
            session_id = request.form.get('session_id')
            student_id = request.form.get('student_id')
            name = request.form.get('name', '')  # Optional
    
            if not session_id or not student_id:
                return jsonify({"error": "Session ID and Student ID are required"}), 400
    
            # Check for existing attendance record
            attendance_ref = db.collection('Sessions').document(f"Session_{session_id}").collection('Attendance').document(f"Student_{student_id}")
            if attendance_ref.get().exists:
                return jsonify({"message": "Attendance already recorded for this student"}), 400
    
            # Store attendance in Firestore
            attendance_ref.set({
                "student_id": student_id,
                "name": name,
                "present": True,  # Default to True since they filled the form
                "timestamp": firestore.SERVER_TIMESTAMP
            })
    
            return jsonify({"message": "Attendance recorded successfully!"}), 200
    
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
