from typing import Annotated

from sqlalchemy.ext.asyncio.session import AsyncSession
from fastapi import APIRouter, Depends, status, Query
from fastapi.exceptions import HTTPException

from app.schemas import note as schema
from app.database import get_db
from app.crud import crud_note

note_router = APIRouter()


@note_router.post(
    path="",
    name="Create note",
    response_model=schema.ResponseNote,
)
async def create_note(
        db: Annotated[AsyncSession, Depends(get_db)],
        note_data: schema.CreateNote,
):

    result = await crud_note.create_note(db=db, note_data=note_data)

    if not result is None:
        return result

    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail="Note creation failed",
    )


@note_router.get(
    path="",
    name="Get notes",
    response_model=schema.ResponseNotes,
)
async def get_notes(
        db: Annotated[AsyncSession, Depends(get_db)],
        page: int = Query(1, ge=1),
        size: int = Query(10, ge=1, le=1000),
):

    offset = (page - 1) * size

    result = await crud_note.get_notes(
        db=db,
        limit=size,
        offset=offset,
    )

    return result


@note_router.put(
    path="/{note_id}",
    name="Update note",
    response_model=schema.ResponseNote,
)
async def update_note(
        db: Annotated[AsyncSession, Depends(get_db)],
        note_id: int,
        update_data: schema.UpdateNote,
):

    result = await crud_note.update_note(
        db=db,
        note_id=note_id,
        update_data=update_data,
    )

    if not result is None:
        return result

    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail="Note update failed",
    )


@note_router.delete(
    path="/{note_id}",
    name="Delete note",
    response_model=bool,
)
async def delete_note(
        db: Annotated[AsyncSession, Depends(get_db)],
        note_id: int,
):

    result = await crud_note.delete_note(
        db=db,
        note_id=note_id,
    )

    if result:
        return result

    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail="Note deletion failed",
    )
