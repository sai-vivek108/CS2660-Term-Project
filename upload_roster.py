import os
import csv
from google.cloud import firestore

# Set the path to your service account key file
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "qrcode-444118-a819b6d831a6.json"

# Initialize Firestore client
db = firestore.Client()

def upload_roster_from_csv(session_id, date, course_name, csv_file_path):
    """
    Upload roster data from a CSV file to Firestore for a specific session.
    
    Args:
        session_id (str): Unique ID for the session.
        date (str): Date and time of the session.
        course_name (str): Name of the course.
        csv_file_path (str): Path to the CSV file containing roster data.
    """
    try:
        # Add session document
        session_ref = db.collection("Sessions").document(f"Session_{session_id}")
        session_ref.set({
            "session_id": session_id,
            "date": date,
            "course_name": course_name
        })
        print(f"Session {session_id} created successfully.")

        # Read roster from CSV and upload to Firestore
        print(f"Uploading roster from {csv_file_path}...")
        with open(csv_file_path, mode='r') as csv_file:
            reader = csv.DictReader(csv_file)
            for row in reader:
                student_id = row['Number']
                name = row['First Name']

                # Add each student to the Attendance subcollection
                student_ref = session_ref.collection("Attendance").document(f"Student_{student_id}")
                student_ref.set({
                    "student_id": student_id,
                    "name": name,
                    "present": False,
                    "timestamp": None
                })
                print(f"Added student: {student_id} - {name}")

        print("Roster uploaded successfully.")
    except Exception as e:
        print(f"An error occurred: {e}")
