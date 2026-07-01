# tests/test_upload.py
from fastapi.testclient import TestClient
from app.main import app  # 3 Only import from app, never from frontend!

client = TestClient(app)

def test_upload_valid_text_file():
    # Simulate a dummy .txt file submission
    file_content = b"Hello World! This is a test runtime string for our upload parser engine."
    response = client.post(
        "/api/upload",
        files={"file": ("test_doc.txt", file_content, "text/plain")}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["filename"] == "test_doc.txt"
    assert data["page_count"] == 1
    assert "Hello World!" in data["preview"]

def test_upload_invalid_file_type():
    # Try sending an unaccepted file type (.png image extension)
    response = client.post(
        "/api/upload",
        files={"file": ("image.png", b"fake_image_bytes", "image/png")}
    )
    assert response.status_code == 400
    assert response.json()["detail"] == "Unsupported file format. Please upload a PDF or TXT file."