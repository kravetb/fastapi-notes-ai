from sqlalchemy.ext.asyncio.session import AsyncSession

from app.schemas import note as schema
from app.models.models import Note, NoteHistory


async def create_note(
        db: AsyncSession,
        note_data: schema.CreateNote
) -> schema.ResponseNote | None:

    try:

        note = Note(
            title=note_data.title,
            content=note_data.content,
        )

        db.add(note)
        await db.commit()
        print("Ok")
        await db.refresh(note)

        note_history = NoteHistory(
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

    except Exception as e:
        print(e)
        await db.rollback()
        return None
