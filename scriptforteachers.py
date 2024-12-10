from datetime import datetime
from upload_roster import upload_roster_from_csv

# Automatically generated session ID and date
session_id = datetime.now().strftime("%Y-%m-%d")
session_date = datetime.now().isoformat() + "Z"

# Prompt teacher for course name and CSV file path
course_name = input("Enter the course name: ")
csv_file_path = input("Enter the path to the roster CSV file: ")

# Call function
upload_roster_from_csv(
    session_id=session_id,
    date=session_date,
    course_name=course_name,
    csv_file_path=csv_file_path
)

print(f"Roster uploaded successfully for session ID: {session_id} at {session_date}")
