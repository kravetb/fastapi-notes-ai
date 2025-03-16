from typing import Annotated, List

from sqlalchemy.ext.asyncio.session import AsyncSession
from fastapi import APIRouter, Depends, status, Query, Path
from fastapi.exceptions import HTTPException

from app.schemas import note as schema
from app.database import get_db
from app.crud import crud_note

note_router = APIRouter()


@note_router.get(
    path="/analytics",
    name="Get analytics",
    response_model=schema.AnalyticsResponse,
)
async def get_analytics(
        db: Annotated[AsyncSession, Depends(get_db)],
):

    result = await crud_note.get_notes_analytics(
        db=db,
    )

    return result


@note_router.post(
    path="",
    name="Create note",
    response_model=schema.ResponseNote,
)
async def create_note(
        db: Annotated[AsyncSession, Depends(get_db)],
        note_data: schema.CreateNote,
):

    try:
        result = await crud_note.create_note(db=db, note_data=note_data)
        return result
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


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
        update_data: schema.UpdateNote,
        note_id: int = Path(..., title="Note ID", description="ID of the note"),
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


@note_router.get(
    path="/{note_id}/history",
    name="Get note history by current note",
    response_model=List[schema.ResponseNoteHistory]
)
async def get_note_history(
        db: Annotated[AsyncSession, Depends(get_db)],
        note_id: int,
):

    result = await crud_note.get_history_by_current_note(db=db, note_id=note_id)

    return result


@note_router.put(
    path="/{note_id}/rollback",
    name="Rollback note to some version",
    response_model=schema.ResponseNote,
)
async def rollback_note(
        db: Annotated[AsyncSession, Depends(get_db)],
        note_id: int,
        data: schema.RollbackNote,
):

    result = await crud_note.roll_back_note(
        db=db,
        note_id=note_id,
        version=data.version,
    )

    if not result is None:
        return result

    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail="Note rollback failed",
    )


@note_router.get(
    path="/{note_id}",
    name="Get detail info about note",
    response_model=schema.DetailResponseNote,
)
async def get_note_detail(
        db: Annotated[AsyncSession, Depends(get_db)],
        note_id: int = Path(..., title="Note ID", description="ID of the note"),
):

    result = await crud_note.get_note_with_history(db=db, note_id=note_id)

    if not result is None:
        return result

    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="Note not found",
    )
