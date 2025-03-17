import pytest
from fastapi.testclient import TestClient
from fastapi import status, HTTPException

from app.crud import crud_note
from app.database import get_db
from app.main import app
from app.tests.fixtures import mock_get_db


@pytest.fixture
def mock_rollback_note():
    async def _mock_rollback_note(db, note_id, version):
        if note_id == 1 and version == 2:
            history = {
                "content": "Restored content",
                "version": 2,
            }
            new_note = {
                "id": note_id,
                "title": "Test",
                "content": history["content"],
                "version": history["version"],
            }
            return new_note

        elif note_id == 999:
            raise HTTPException(status_code=404, detail="Note not found")

        raise Exception("Database error")

    return _mock_rollback_note


@pytest.mark.asyncio
async def test_rollback_note_success(mock_get_db, mock_rollback_note):
    app.dependency_overrides[get_db] = lambda: mock_get_db
    crud_note.roll_back_note = mock_rollback_note

    client = TestClient(app)
    note_id = 1
    data = {"version": 2}
    response = client.put(f"/notes/{note_id}/rollback", json=data)

    assert response.status_code == 200
    assert response.json() == {"id": note_id, "title": "Test", "version": 2, "content": "Restored content"}


@pytest.mark.asyncio
async def test_rollback_note_not_found(mock_get_db, mock_rollback_note):
    app.dependency_overrides[get_db] = lambda: mock_get_db
    crud_note.roll_back_note = mock_rollback_note

    client = TestClient(app)
    note_id = 999
    data = {"version": 2}
    response = client.put(f"/notes/{note_id}/rollback", json=data)

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json() == {"detail": "Note not found"}


@pytest.mark.asyncio
async def test_rollback_note_invalid_id(mock_get_db):
    app.dependency_overrides[get_db] = lambda: mock_get_db

    client = TestClient(app)
    response = client.put("/notes/abc/rollback", json={"version": 2})

    assert response.status_code == 422
    assert "detail" in response.json()


@pytest.mark.asyncio
async def test_rollback_note_db_error(mock_get_db, mock_rollback_note):
    app.dependency_overrides[get_db] = lambda: mock_get_db
    crud_note.roll_back_note = mock_rollback_note

    client = TestClient(app)
    note_id = 500
    data = {"version": 2}
    response = client.put(f"/notes/{note_id}/rollback", json=data)

    assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
    assert response.json() == {"detail": "Internal server error"}
