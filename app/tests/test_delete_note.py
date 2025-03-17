import pytest
from fastapi.testclient import TestClient
from fastapi import status, HTTPException

from app.crud import crud_note
from app.database import get_db
from app.main import app
from app.tests.fixtures import mock_get_db


@pytest.fixture
def mock_delete_note():
    async def _mock_delete_note(db, note_id):
        if note_id == 1:
            return True
        elif note_id == 999:
            raise HTTPException(status_code=404, detail="Note not found")
        raise Exception("Database error")
    return _mock_delete_note


@pytest.mark.asyncio
async def test_delete_note_success(mock_get_db, mock_delete_note):
    app.dependency_overrides[get_db] = lambda: mock_get_db
    crud_note.delete_note = mock_delete_note

    client = TestClient(app)
    note_id = 1
    response = client.delete(f"/notes/{note_id}")

    assert response.status_code == 200
    assert response.json() is True


@pytest.mark.asyncio
async def test_delete_note_not_found(mock_get_db, mock_delete_note):
    app.dependency_overrides[get_db] = lambda: mock_get_db
    crud_note.delete_note = mock_delete_note

    client = TestClient(app)
    note_id = 999
    response = client.delete(f"/notes/{note_id}")

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json() == {"detail": "Note not found"}


@pytest.mark.asyncio
async def test_delete_note_invalid_id(mock_get_db):
    app.dependency_overrides[get_db] = lambda: mock_get_db

    client = TestClient(app)
    response = client.delete("/notes/abc")

    assert response.status_code == 422
    assert "detail" in response.json()


@pytest.mark.asyncio
async def test_delete_note_db_error(mock_get_db, mock_delete_note):
    app.dependency_overrides[get_db] = lambda: mock_get_db
    crud_note.delete_note = mock_delete_note

    client = TestClient(app)
    note_id = 500
    response = client.delete(f"/notes/{note_id}")

    assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
    assert response.json() == {"detail": "Internal server error"}
