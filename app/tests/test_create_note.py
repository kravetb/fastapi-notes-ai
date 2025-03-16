import pytest
from unittest.mock import AsyncMock

from fastapi.testclient import TestClient
from fastapi import status

from app.crud import crud_note
from app.database import get_db
from app.main import app
from app import models
from app.schemas import note as schema
from app.tests.fixtures import mock_get_db


@pytest.fixture
def mock_create_note():
    async def _mock_create_note(db, note_data):

        note = models.models.Note(
            id=1,
            title=note_data.title,
            content=note_data.content,
            version=1,
        )

        db.add(note)
        await db.commit()
        await db.refresh(note)

        note_history = models.models.NoteHistory(
            content=note.content,
            version=note.version,
            note_id=note.id,
        )

        db.add(note_history)
        await db.commit()

        note_response = schema.ResponseNote(
            id=note.id,
            title=note.title,
            content=note.content,
            version=note.version,
        )

        return note_response

    return _mock_create_note


@pytest.mark.asyncio
async def test_create_note_success(mock_get_db, mock_create_note):

    app.dependency_overrides[get_db] = lambda: mock_get_db

    crud_note.create_note = mock_create_note
    note_data = schema.CreateNote(title="Test Title", content="Test Content")

    client = TestClient(app)
    response = client.post("/notes", json=note_data.dict())

    assert response.status_code == 200
    assert response.json()["title"] == "Test Title"
    assert response.json()["content"] == "Test Content"
    assert "id" in response.json()
    assert "version" in response.json()


@pytest.mark.asyncio
async def test_create_note_failure(mock_get_db):

    app.dependency_overrides[get_db] = lambda: mock_get_db

    crud_note.create_note = AsyncMock(side_effect=Exception("Database error"))

    note_data = schema.CreateNote(title="Test Title", content="Test Content")

    client = TestClient(app)

    response = client.post("/notes", json=note_data.dict())

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json() == {"detail": "Database error"}


@pytest.mark.asyncio
async def test_create_note_validation_error(mock_get_db, mock_create_note):

    app.dependency_overrides[get_db] = lambda: mock_get_db

    crud_note.create_note = mock_create_note
    invalid_note_data = {"title": 3, "content": 9}

    client = TestClient(app)
    response = client.post("/notes", json=invalid_note_data)

    assert response.status_code == 422
    assert "detail" in response.json()
    assert len(response.json()["detail"]) > 0
