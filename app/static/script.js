document.getElementById('generateQRButton').addEventListener('click', function () {
    const currentDate = new Date().toISOString().split('T')[0];
    const session_id = `session-${currentDate}`;

    const data = {
        session_id: session_id,
        course_name: 'CS1660_test',
        date: currentDate
    };

    fetch('/generate', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(data)
    })
        .then(response => response.json())
        .then(data => {
            if (data.message) {
                alert(data.message);
            } else {
                alert('Error: ' + data.error);
            }
        })
        .catch(error => {
            alert('An error occurred: ' + error.message);
        });
});

function submitAttendance() {
    const studentId = document.getElementById('student_id').value;
    if (!studentId) {
        alert("Please enter your Student ID.");
        return;
    }

    fetch('/submit_attendance', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ student_id: studentId, date: "{{ current_date }}" })
    })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                alert("Attendance submitted successfully!");
                window.location.href = "/";
            } else {
                alert("Error submitting attendance.");
            }
        })
        .catch(error => {
            console.error('Error:', error);
            alert("There was an error with your request.");
        });
}

function setSubmitAttendanceLink() {
    const currentDate = new Date().toISOString().split('T')[0];
    const sessionId = `session-${currentDate}`;
    const submitButton = document.getElementById('submitAttendanceButton');

    if (submitButton) {
        submitButton.href = `/attendance/form/${sessionId}`;
    }
}

document.addEventListener('DOMContentLoaded', setSubmitAttendanceLink);