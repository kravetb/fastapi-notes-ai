from unittest.mock import AsyncMock

import pytest
from sqlalchemy.ext.asyncio import AsyncSession


@pytest.fixture
def mock_get_db():
    mock_db = AsyncMock(spec=AsyncSession)
    return mock_db
