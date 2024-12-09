import qrcode
from datetime import datetime
from google.cloud import storage
import os
import tempfile

BUCKET_NAME = "qr-attendance-bucket"

def generate_qr_code(session_id):
    try:
        # service_account_key_path = r"clear-practice-435922-q9-66e79325057d.json"
        # if not os.path.exists(service_account_key_path):
            # return "Service account key file not found.", 500
        
        # Authenticate
        storage_client = storage.Client()
        # storage.Client.from_service_account_json(service_account_key_path)
        
        # session_id = f"session-{datetime.now().strftime('%Y-%m-%d')}"
        # this needs to direct the student to the attendance form.
        qr_content = f"{request.host_url}attendance/form/{session_id}"

        # Generate QR code
        qr = qrcode.QRCode(version=1, box_size=10, border=4)
        qr.add_data(qr_content)
        qr.make(fit=True)
        img = qr.make_image(fill="black", back_color="white")

        # Save the QR code image to a temporary file
        # qr_file_path = f"/tmp/{session_id}.png"
        # img.save(qr_file_path)

        # # Upload the QR code to Cloud Storage
        # bucket = storage_client.bucket(BUCKET_NAME)
        # blob = bucket.blob(f"{session_id}.png")
        # blob.upload_from_filename(qr_file_path)

        # return f"QR Code generated: {blob.public_url}", 200

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