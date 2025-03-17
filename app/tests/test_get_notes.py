import pytest
from fastapi.testclient import TestClient

from app.crud import crud_note
from app.database import get_db
from app.main import app
from app.models import models
from app.schemas import note as schema
from app.tests.fixtures import mock_get_db
from app.ai_service import ai_service


@pytest.fixture
def mock_get_notes():
    async def _mock_get_notes(db, limit, offset):
        notes = [
            models.Note(id=i, title=f"Title {i}", content=f"Content {i}", version=1)
            for i in range(1, limit + 1)
        ]
        return schema.ResponseNotes(
            notes=[
                schema.ResponseNote(
                    id=item.id,
                    version=item.version,
                    title=item.title,
                    content=f"Summarized Content {item.id}",
                )
                for item in notes
            ],
            count_items=50,
        )

    return _mock_get_notes


@pytest.fixture
def mock_summarize_note():
    async def _mock_summarize_note(note_content: str):
        return f"Summarized {note_content}"

    return _mock_summarize_note


@pytest.mark.asyncio
async def test_get_notes_success(mock_get_db, mock_get_notes, mock_summarize_note):
    app.dependency_overrides[get_db] = lambda: mock_get_db
    crud_note.get_notes = mock_get_notes
    ai_service.get_summarize_note = mock_summarize_note

    client = TestClient(app)
    response = client.get("/notes?page=1&size=5")

    assert response.status_code == 200
    assert response.json()["count_items"] == 50
    assert len(response.json()["notes"]) == 5
    assert response.json()["notes"][0]["content"].startswith("Summarized")


@pytest.mark.asyncio
async def test_get_notes_invalid_pagination(mock_get_db):
    app.dependency_overrides[get_db] = lambda: mock_get_db
    client = TestClient(app)

    response = client.get("/notes?page=-1&size=10")
    assert response.status_code == 422

    response = client.get("/notes?page=1&size=1001")
    assert response.status_code == 422
