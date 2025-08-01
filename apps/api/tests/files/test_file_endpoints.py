import io
from fastapi.testclient import TestClient
from models import FileUpload


class TestFileEndpoints:
    def test_upload_and_download(self, client: TestClient, session, auth_headers_volunteer):
        data = {"category": "general"}
        file_content = b"dummy pdf content"
        files = {"file": ("test.pdf", io.BytesIO(file_content), "application/pdf")}
        resp = client.post("/v1/files/upload", data=data, files=files, headers=auth_headers_volunteer)
        assert resp.status_code == 200
        file_id = resp.json()["id"]

        db_obj = session.get(FileUpload, file_id)
        assert db_obj is not None

        resp = client.get(f"/v1/files/{file_id}", headers=auth_headers_volunteer)
        assert resp.status_code == 200
        assert resp.content == file_content
