import pytest
from fastapi.testclient import TestClient

from app.crud import crud_note
from app.database import get_db
from app.main import app
from app.tests.fixtures import mock_get_db


@pytest.fixture
def mock_get_analytics():
    async def _mock_get_analytics(db):
        # Мок для даних аналітики
        notes = [
            {"content": "This is the first note."},
            {"content": "This is the second note."},
            {"content": "Short note."}
        ]
        total_words = 10
        average_note_length = 5.0
        most_common_words = [['note', 3], ['the', 2]]
        shortest_notes = ["Short note."]
        longest_notes = ["This is the first note.", "This is the second note."]
        return {
            "total_words": total_words,
            "average_note_length": average_note_length,
            "most_common_words": most_common_words,
            "shortest_notes": shortest_notes,
            "longest_notes": longest_notes,
        }

    return _mock_get_analytics


@pytest.mark.asyncio
async def test_get_analytics_success(mock_get_db, mock_get_analytics):
    app.dependency_overrides[get_db] = lambda: mock_get_db
    crud_note.get_notes_analytics = mock_get_analytics

    client = TestClient(app)
    response = client.get("/notes/analytics")

    assert response.status_code == 200
    data = response.json()
    assert data["total_words"] == 10
    assert data["average_note_length"] == 5.0
    assert data["most_common_words"] == [['note', 3], ['the', 2]]
    assert data["shortest_notes"] == ["Short note."]
    assert data["longest_notes"] == ["This is the first note.", "This is the second note."]


@pytest.mark.asyncio
async def test_get_analytics_empty(mock_get_db):
    app.dependency_overrides[get_db] = lambda: mock_get_db

    async def _mock_get_empty_analytics(db):
        return {
            "total_words": 0,
            "average_note_length": 0,
            "most_common_words": [],
            "shortest_notes": [],
            "longest_notes": [],
        }

    crud_note.get_notes_analytics = _mock_get_empty_analytics

    client = TestClient(app)
    response = client.get("/notes/analytics")

    assert response.status_code == 200
    data = response.json()
    assert data["total_words"] == 0
    assert data["average_note_length"] == 0
    assert data["most_common_words"] == []
    assert data["shortest_notes"] == []
    assert data["longest_notes"] == []
