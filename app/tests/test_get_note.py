import pytest

from fastapi.testclient import TestClient
from fastapi import status

from app.crud import crud_note
from app.database import get_db
from app.main import app
from app.models import models
from app.schemas import note as schema
from app.tests.fixtures import mock_get_db


@pytest.fixture
def mock_get_note_with_history():
    async def _mock_get_note_with_history(db, note_id):
        if note_id == 1:
            note = models.Note(
                id=1,
                title="Test Title",
                content="Test Content",
                version=1,
                histories=[
                    models.NoteHistory(
                        id=1,
                        content="Old content",
                        version=1,
                        updated_at="2023-03-16T00:00:00",
                    )
                ]
            )
            return schema.DetailResponseNote(
                id=note.id,
                title=note.title,
                content=note.content,
                version=note.version,
                history=[
                    schema.ResponseNoteHistory(
                        id=item.id,
                        version=item.version,
                        content=item.content,
                        updated_at=item.updated_at,
                    ) for item in note.histories
                ]
            )

        return None

    return _mock_get_note_with_history


@pytest.mark.asyncio
async def test_get_note_success(mock_get_db, mock_get_note_with_history):

    app.dependency_overrides[get_db] = lambda: mock_get_db

    crud_note.get_note_with_history = mock_get_note_with_history
    note_id = 1

    client = TestClient(app)
    response = client.get(f"/notes/{note_id}")

    assert response.status_code == 200
    assert response.json()["title"] == "Test Title"
    assert response.json()["content"] == "Test Content"
    assert response.json()["version"] == 1
    assert response.json()["id"] == note_id
    assert len(response.json()["history"]) == 1
    assert response.json()["history"][0]["content"] == "Old content"
    assert response.json()["history"][0]["version"] == 1


@pytest.mark.asyncio
async def test_get_note_not_found(mock_get_db, mock_get_note_with_history):

    app.dependency_overrides[get_db] = lambda: mock_get_db

    crud_note.get_note_with_history = mock_get_note_with_history
    note_id = 999

    client = TestClient(app)
    response = client.get(f"/notes/{note_id}")

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json() == {"detail": "Note not found"}


@pytest.mark.asyncio
async def test_get_note_validation_error(mock_get_db):

    app.dependency_overrides[get_db] = lambda: mock_get_db

    client = TestClient(app)
    response = client.get("/notes/abc")

    assert response.status_code == 422
    assert "detail" in response.json()
    assert len(response.json()["detail"]) > 0
