from typing import Annotated

from sqlalchemy.ext.asyncio.session import AsyncSession
from fastapi import APIRouter, Depends, status
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



