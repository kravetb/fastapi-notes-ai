from datetime import datetime
from typing import List

from pydantic import BaseModel, ConfigDict, Field


class Base(BaseModel):
    model_config = ConfigDict(from_attributes=True)


class Note(Base):
    title: str = Field(
        ...,
        description="The title of the note",
        example="Note-1",
    )
    content: str = Field(
        ...,
        description="The content of the note",
        example="Test note for test task",
    )


class CreateNote(Note):
    pass


class ResponseNote(Note):
    id: int = Field(
        ...,
        description="The id of the note",
        example=1,
    )
    version: int = Field(
        ...,
        description="The version of the note",
        example=3,
    )


class ResponseNotes(Base):
    notes: List[ResponseNote] = Field(
        ...,
        description="List with ResponseNote instances",
    )
    count_items: int = Field(
        ...,
        description="The count of items in database",
        example=56,
    )


class UpdateNote(Base):
    content: str = Field(
        ...,
        description="New content by current note",
        example="New test content",
    )


class ResponseNoteHistory(Base):
    id: int = Field(
        ...,
        description="The id of the note history item",
        example=4,
    )
    version: int = Field(
        ...,
        description="The version of the note history item",
        example=2,
    )
    content: str = Field(
        ...,
        description="The content of the note history item",
        example="Test history content",
    )
    updated_at: datetime = Field(
        ...,
        description="The time when the note item was updated",
        example="2025-03-15 12:00:00",
    )


class RollbackNote(Base):
    version: int = Field(
        ...,
        description="The old version of the note history item",
        example=2,
    )
