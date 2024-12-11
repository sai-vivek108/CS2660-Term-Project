from flask import request, jsonify, render_template
from google.cloud import firestore
from app.models import record_attendance
from google.cloud import storage
from datetime import datetime
import csv

BUCKET_NAME = "qr-attendance-bucket"


# helper function
def get_session_details():
    
    current_date = datetime.now().strftime('%Y-%m-%d')
    session_id = f"session-{current_date}"
    course_name = "cs1660"
    return current_date, session_id, course_name

def setup_routes(app):
    @app.route('/')
    def home():
        return render_template('home.html')

    @app.route('/attendance/form/<session_id>/<course_name>', methods=['GET'])
    def attendance_form(session_id, course_name):
        return render_template('attendance_form.html', current_date=session_id.split("session-")[1], session_id= session_id, course_name=course_name)

    @app.route('/qrCode', methods=['GET'])
    def display_qrCode():
        try:
            current_date, session_id, _ = get_session_details()
            qr_url = f"https://storage.googleapis.com/qr-attendance-bucket/{session_id}.png"
            
            return render_template('qrCode.html', qr_url=qr_url, current_date=current_date)
        
        except Exception as e:
            return jsonify({"error": str(e)}), 500

    @app.route('/submit_attendance', methods=['POST'])
    def submit_attendance():
        try:
            # Get form data
            _, session_id, _ = get_session_details()
            student_id = request.form.get('student_id')
            course_name = request.form.get('course_name')
            present = True  # Since student scanned the QR
    
            if not session_id or not student_id:
                return render_template('attendance_result.html', success=False, message="Session ID and Student ID are required.")
    
            # Record the attendance 
            response, status_code = record_attendance(session_id, student_id, course_name, present)
    
            if status_code == 200:
                return render_template('attendance_result.html', success=True, message=response.get('message', 'Attendance recorded successfully'))
            else:
                return render_template('attendance_result.html', success=False, message=response.get('error', 'An error occurred.'))
    
        except Exception as e:
            return render_template('attendance_result.html', success=False, message=f"An error occurred: {str(e)}")

    @app.route('/attendance', methods=['GET'])
    def get_attendance():
        """
        Fetch attendance records for a specific session.
        """
        db = firestore.Client()  # Initialize Firestore client
        _,session_id,course_name = get_session_details()      
        try:
            # print("At DB collections: \t", db.collection('Sessions'))
            attendance_ref = db.collection('Sessions').document(f"{course_name}").collection(f"{session_id}")
            
            # Query all attendance records in the subcollection
            attendance_docs = attendance_ref.stream()

            # Compile attendance data into a list
            attendance_records = []
            for doc in attendance_docs:
                record = doc.to_dict()
                attendance_records.append(record)

            return render_template('attendance.html', session_id=session_id, attendance_records=attendance_records)

        except Exception as e:
            return jsonify({"error": str(e)}), 500

    @app.route('/add_students', methods=['GET'])
    def add_students_form():
        """
        Serve the form to add students to a course.
        """
        return render_template('add_students.html')

    @app.route('/upload_students', methods=['POST'])
    def upload_students():
        """
        Handle CSV upload, process student IDs, and store them in Firestore.
        """
        db = firestore.Client()  # Initialize Firestore client
        try:
            # Get course_name and start_date from the form
            course_name = request.form.get('course_name')
            start_date_str = request.form.get('start_date')  # 'YYYY-MM-DDTHH:MM' format
            if not course_name or not start_date_str:
                return render_template('upload_result.html', success=False, message="Course name and start date are required.")
            
            # Convert start_date to a datetime object
            start_date = datetime.strptime(start_date_str, '%Y-%m-%dT%H:%M')

            # Validate that start_date is in the future
            current_time = datetime.utcnow()
            if start_date <= current_time:
                return render_template('upload_result.html', success=False, message="Start date must be greater than the current time.")

            # Get the uploaded file
            file = request.files.get('file')
            if not file:
                return render_template('upload_result.html', success=False, message="CSV file is required")

            # Parse the CSV file
            student_ids = []
            csv_reader = csv.reader(file.stream.read().decode('utf-8').splitlines())
            for row in csv_reader:
                if row:  # Avoid empty rows
                    student_ids.append(row[0])  # Assuming each row contains one student ID

            # Store course metadata and student IDs in Firestore
            course_ref = db.collection('Sessions').document(course_name)
            course_ref.set({
                "course_name": course_name,
                "start_date": start_date,  # Save start date
            })

            # Add each student ID to the 'Students' subcollection
            for student_id in student_ids:
                student_ref = course_ref.collection('Students').document(student_id)
                student_ref.set({"student_id": student_id})

            return render_template('upload_result.html', success=True, message=f"Successfully added {len(student_ids)} students to course {course_name} with start date {start_date}")

        except Exception as e:
            return render_template('upload_result.html', success=False, message=f"An error occurred: {str(e)}")