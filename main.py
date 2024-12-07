import qrcode
from datetime import datetime
from google.cloud import storage

BUCKET_NAME = "attendance-qr-bucket"

def generate_qr_code(request):
    session_id = f"session-{datetime.now().strftime('%Y-%m-%d')}"
    qr_content = f"https://storage.googleapis.com/attendance-qr-bucket/{session_id}.png"

    qr = qrcode.QRCode(version=1, box_size=10, border=4)
    qr.add_data(qr_content)
    qr.make(fit=True)
    img = qr.make_image(fill="black", back_color="white")

    qr_file_path = f"/tmp/{session_id}.png"
    img.save(qr_file_path)

    storage_client = storage.Client()
    bucket = storage_client.bucket(BUCKET_NAME)
    blob = bucket.blob(f"{session_id}.png")
    blob.upload_from_filename(qr_file_path)

    blob.make_public()
    return f"QR Code generated: {blob.public_url}", 200
