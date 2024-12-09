from google.cloud import firestore
from google.oauth2 import service_account

# db = firestore.Client()
# service_account_path = r"clear-practice-435922-q9-66e79325057d.json"
# credentials = service_account.Credentials.from_service_account_file(service_account_path)
db = firestore.Client(project='clear-practice-435922-q9')

# test
def add_session(session_id, course_name, date):
    session_ref = db.collection('Sessions').document(f"Session_{session_id}")
    if session_ref.get().exists:
        return {"message": "Attendance already recorded"}, 400
    else:
        session_ref.set({
            "session_id": session_id,
            "course_name": course_name,
            "date": date,
        })
    return {"message": "Session added successfully!"}, 200

def record_attendance(session_id, student_id, name, present):
    attendance_ref = db.collection('Sessions').document(f"Session_{session_id}").collection('Attendance').document(f"Student_{student_id}")
    if attendance_ref.get().exists:
        return {"message": "Attendance already recorded"}, 400
    else:
        attendance_ref.set({
            "student_id": student_id,
            "name": name,# can be optional
            "present": present,
            "timestamp": firestore.SERVER_TIMESTAMP
        })
    return {"message": "Attendance recorded successfully!"}, 200
