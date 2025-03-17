import pytest
from fastapi.testclient import TestClient
from fastapi import status, HTTPException

from app.crud import crud_note
from app.database import get_db
from app.main import app
from app.schemas import note as schema
from app.tests.fixtures import mock_get_db


@pytest.fixture
def mock_update_note():
    async def _mock_update_note(db, note_id, update_data):
        if note_id == 1:
            return schema.ResponseNote(
                id=1,
                title="Sample Title",
                content=update_data.content,
                version=2
            )
        elif note_id == 999:
            raise HTTPException(status_code=404, detail="Note not found")

        raise HTTPException(status_code=500, detail="Database error")

    return _mock_update_note


@pytest.mark.asyncio
async def test_update_note_success(mock_get_db, mock_update_note):
    app.dependency_overrides[get_db] = lambda: mock_get_db
    crud_note.update_note = mock_update_note

    client = TestClient(app)
    note_id = 1
    payload = {"content": "Updated Content"}

    response = client.put(f"/notes/{note_id}", json=payload)

    assert response.status_code == 200
    assert response.json()["id"] == note_id
    assert response.json()["content"] == "Updated Content"
    assert response.json()["version"] == 2


@pytest.mark.asyncio
async def test_update_note_not_found(mock_get_db, mock_update_note):
    app.dependency_overrides[get_db] = lambda: mock_get_db
    crud_note.update_note = mock_update_note

    client = TestClient(app)
    note_id = 999
    payload = {"content": "Updated Content"}

    response = client.put(f"/notes/{note_id}", json=payload)

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json() == {"detail": "Note not found"}


@pytest.mark.asyncio
async def test_update_note_invalid_id(mock_get_db):
    app.dependency_overrides[get_db] = lambda: mock_get_db

    client = TestClient(app)
    response = client.put("/notes/abc", json={"content": "Updated Content"})

    assert response.status_code == 422
    assert "detail" in response.json()


@pytest.mark.asyncio
async def test_update_note_db_error(mock_get_db, mock_update_note):
    app.dependency_overrides[get_db] = lambda: mock_get_db
    crud_note.update_note = mock_update_note

    client = TestClient(app)
    note_id = 500
    payload = {"content": "Updated Content"}

    response = client.put(f"/notes/{note_id}", json=payload)

    assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
    assert "Database error" in response.json()["detail"]
