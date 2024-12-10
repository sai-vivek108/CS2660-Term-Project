import qrcode
from datetime import datetime, timedelta
from google.cloud import storage, firestore
import os
import tempfile
from flask import request
import functions_framework


BUCKET_NAME = "qr-attendance-bucket"

def generate_qr_code(session_id, course_name):
    try:
        # service_account_key_path = r"clear-practice-435922-q9-66e79325057d.json"
        # if not os.path.exists(service_account_key_path):
            # return "Service account key file not found.", 500
        
        # Authenticate
        storage_client = storage.Client()
        # storage.Client.from_service_account_json(service_account_key_path)
        
        session_id = f"session-{datetime.now().strftime('%Y-%m-%d')}"
        # this needs to direct the student to the attendance form.
        qr_content = f"{request.host_url}attendance/form/{session_id}"

        # Generate QR code
        qr = qrcode.QRCode(version=1, box_size=10, border=4)
        qr.add_data(qr_content)
        qr.make(fit=True)
        img = qr.make_image(fill="black", back_color="white")

        # Save the QR code image to a temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as tmp_file:
            qr_file_path = tmp_file.name  # Get the file path from tempfile

            # Save the QR code image to the temporary file
            img.save(qr_file_path)

            # Upload the QR code to Cloud Storage
            bucket = storage_client.bucket(BUCKET_NAME)
            blob = bucket.blob(f"{session_id}.png")
            blob.upload_from_filename(qr_file_path)

            # cleaning up
            os.unlink(qr_file_path)
            return f"QR Code generated successfully: {blob.public_url}", 200

    except Exception as e:
        # Catching any other exceptions and providing a message
        return f"An error occurred: {str(e)}", 500
# generate_qr_code(1)
@functions_framework.cloud_event
def scheduled_qr_generator(cloud_event):
    """
    Cloud Function triggered by Pub/Sub for scheduled QR code generation.
    """
    try:
        # Parse the Pub/Sub message
        data = cloud_event.data
        print(f"Pub/Sub message received: {data}")

        # Initialize Firestore client
        db = firestore.Client()
        current_time = datetime.utcnow()
        sessions_ref = db.collection("Sessions")
        sessions = sessions_ref.stream()

        for session in sessions:
            session_data = session.to_dict()
            session_id = session.id
            course_name = session_data.get("course_name")
            start_date = session_data.get("start_date")

            if not start_date:
                continue

            # Convert Firestore timestamp to datetime
            start_date = start_date.replace(tzinfo=None)
            next_qr_time = start_date
            while next_qr_time < current_time:
                next_qr_time += timedelta(days=1)

            if current_time >= next_qr_time - timedelta(minutes=5):
                qr_url = generate_qr_code(session_id, course_name)
                print(f"Generated QR code for session {session_id}: {qr_url}")

                # Copy student fields from `Students` subcollection
                students_ref = db.collection("Sessions").document(course_name).collection("Students")
                students = students_ref.stream()

                for student in students:
                    student_data = student.to_dict()
                    student_id = student_data.get("student_id")

                    # Add student to the session's attendance subcollection
                    attendance_ref = db.collection("Sessions").document(course_name).collection(session_id).document(f"Student_{student_id}")
                    attendance_ref.set({
                        "student_id": student_id,
                        # "name": student_data.get("name", ""),  # Optional
                        "present": False,
                        "timestamp": ""
                    })

    except Exception as e:
        print(f"An error occurred: {e}")
