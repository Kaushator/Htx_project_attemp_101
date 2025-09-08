import pytest
from fastapi.testclient import TestClient
from starlette.status import HTTP_200_OK, HTTP_400_BAD_REQUEST
from app.main import app
from pathlib import Path
import io

# Fixture for the test client
@pytest.fixture(scope="module")
def client():
    with TestClient(app) as c:
        yield c

# Fixture for a sample CSV file
@pytest.fixture
def sample_csv_file():
    csv_content = "Date,Symbol,Side,Amount,Price,Fee\n2023-01-01,BTCUSDT,buy,0.1,50000,0.001"
    return ("test.csv", io.BytesIO(csv_content.encode('utf-8')), "text/csv")

# Fixture for a sample Excel file
@pytest.fixture
def sample_excel_file(tmp_path: Path):
    import pandas as pd
    file_path = tmp_path / "test.xlsx"
    df = pd.DataFrame({
        'Date': ['2023-01-01'], 'Symbol': ['BTCUSDT'], 'Side': ['buy'],
        'Amount': [0.1], 'Price': [50000], 'Fee': [0.001]
    })
    df.to_excel(file_path, index=False, engine='openpyxl')
    return ("test.xlsx", open(file_path, "rb"), "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

def test_upload_csv_success(client, sample_csv_file):
    """Test successful CSV file upload."""
    response = client.post("/api/v1/files/upload", files={"file": sample_csv_file})
    assert response.status_code == HTTP_200_OK
    json_response = response.json()
    assert json_response["filename"] == "test.csv"
    assert json_response["status"] == "processing"
    assert json_response["message"] == "File uploaded successfully"

def test_upload_excel_success(client, sample_excel_file):
    """Test successful Excel file upload."""
    response = client.post("/api/v1/files/upload", files={"file": sample_excel_file})
    assert response.status_code == HTTP_200_OK
    json_response = response.json()
    assert json_response["filename"] == "test.xlsx"
    assert json_response["status"] == "processing"
    assert json_response["message"] == "File uploaded successfully"

def test_upload_unsupported_file_type(client):
    """Test uploading a file with an unsupported extension."""
    unsupported_file = ("test.txt", io.BytesIO(b"some text data"), "text/plain")
    response = client.post("/api/v1/files/upload", files={"file": unsupported_file})
    assert response.status_code == HTTP_400_BAD_REQUEST
    assert "File type not allowed" in response.json()["detail"]

def test_upload_no_file(client):
    """Test request with no file attached."""
    response = client.post("/api/v1/files/upload")
    assert response.status_code != HTTP_200_OK # Should be 422 or similar
    assert "Field required" in response.text
