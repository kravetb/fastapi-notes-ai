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
        description="The versio of the note",
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
