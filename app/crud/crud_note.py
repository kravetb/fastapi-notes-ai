from collections import Counter
from typing import List

from fastapi import HTTPException
from sqlalchemy.ext.asyncio.session import AsyncSession
from sqlalchemy import select, func, update, delete
from sqlalchemy.orm import joinedload
import nltk
import numpy as np

from app.schemas import note as schema
from app.models.models import Note, NoteHistory
from app.ai_service import ai_service


async def get_note(
        db: AsyncSession,
        note_id: int,
):

    query = select(Note).where(Note.id == note_id)

    result = await db.execute(query)
    note_data = result.scalar()

    if note_data is None:
        return None

    note = schema.ResponseNote(
        id=note_data.id,
        version=note_data.version,
        title=note_data.title,
        content=note_data.content,
    )

    return note


async def check_note(
        db: AsyncSession,
        note_id: int,
):
    query = select(Note).where(Note.id == note_id)
    result = await db.execute(query)
    note_data = result.scalar()
    if note_data is None:
        return False

    return True


async def get_note_with_history(
        db: AsyncSession,
        note_id: int,
) -> schema.DetailResponseNote | None:

    query = (
        select(Note)
        .options(
            joinedload(Note.histories),
        )
        .where(Note.id == note_id)
    )

    result = await db.execute(query)
    note_data = result.scalar()

    if note_data is None:
        return None

    note = schema.DetailResponseNote(
        id=note_data.id,
        version=note_data.version,
        title=note_data.title,
        content=note_data.content,
        history=[
            schema.ResponseNoteHistory(
                id=item.id,
                version=item.version,
                content=item.content,
                updated_at=item.updated_at,
            )
            for item in note_data.histories
        ]
    )

    return note


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
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")


async def get_notes(
        db: AsyncSession,
        limit: int = 10,
        offset: int = 0,
):

    query = (
        select(Note)
        .limit(limit)
        .offset(offset)
    )
    count_query = select(func.count(Note.id))

    result = await db.execute(query)
    notes_data = result.scalars().all()

    count_result = await db.execute(count_query)
    count = count_result.scalar()

    notes_response = schema.ResponseNotes(
        notes=[
            schema.ResponseNote(
                id=item.id,
                version=item.version,
                title=item.title,
                content= await ai_service.get_summarize_note(item.content),
            )
            for item in notes_data
        ],
        count_items=count,
    )

    return notes_response


async def update_note(
        db: AsyncSession,
        note_id: int,
        update_data: schema.UpdateNote,
) -> schema.ResponseNote | None:

    try:
        try:
            note_query = (
                update(Note)
                .where(Note.id == note_id)
                .values(
                    content=update_data.content,
                    version=Note.version + 1,
                )
                .returning(Note.version)
            )

            result = await db.execute(note_query)
            new_version = result.scalar()

        except Exception:
            await db.rollback()
            raise HTTPException(status_code=404, detail="Note not found")


        note_history = NoteHistory(
            content=update_data.content,
            version=new_version,
            note_id=note_id,
        )

        db.add(note_history)

        await db.commit()

        new_note = await get_note(db=db, note_id=note_id)

        return new_note

    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")


async def delete_note(db: AsyncSession, note_id: int) -> bool:

    try:

        delete_query = delete(Note).where(Note.id == note_id)
        await db.execute(delete_query)
        await db.commit()

        return True

    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")


async def get_history_by_current_note(
        db: AsyncSession,
        note_id: int,
) -> List[schema.ResponseNoteHistory]:

    query = select(NoteHistory).where(NoteHistory.note_id == note_id)
    result = await db.execute(query)
    histories_data = result.scalars().all()

    histories_response = [
        schema.ResponseNoteHistory(
            id=item.id,
            version=item.version,
            content=item.content,
            updated_at=item.updated_at,
        )
        for item in histories_data
    ]

    return histories_response


async def roll_back_note(
        db: AsyncSession,
        note_id: int,
        version: int,
):

    try:
        get_history_query = (
            select(NoteHistory)
            .where(
                NoteHistory.note_id == note_id,
                NoteHistory.version == version,
            )
        )

        history_result = await db.execute(get_history_query)
        history = history_result.scalar()

        update_note_query = (
            update(Note)
            .where(Note.id == note_id)
            .values(
                content=history.content,
                version=history.version,
            )
        )

        await db.execute(update_note_query)
        await db.commit()

        new_note = await get_note(db=db, note_id=note_id)

        return new_note

    except Exception:
        await db.rollback()
        return None


async def get_notes_analytics(db: AsyncSession):
    query = select(Note)
    result = await db.execute(query)
    notes = result.scalars().all()

    if not notes:
        return schema.AnalyticsResponse()

    texts = [note.content for note in notes]

    all_text = " ".join(texts)

    words = nltk.word_tokenize(all_text)

    filtered_words = [word for word in words if word.isalpha()]

    total_words = len(filtered_words)

    note_lengths = [len([word for word in nltk.word_tokenize(text) if word.isalpha()]) for text in texts]
    avg_length = np.mean(note_lengths)

    word_counts = Counter(filtered_words)
    most_common_words = word_counts.most_common(5)

    sorted_notes = sorted(notes, key=lambda note: len(note.content))

    shortest_notes = [note.content for note in sorted_notes[:3]]
    longest_notes = [note.content for note in sorted_notes[-3:]]

    response = schema.AnalyticsResponse(
        total_words=total_words,
        average_note_length=avg_length,
        most_common_words=most_common_words,
        shortest_notes=shortest_notes,
        longest_notes=longest_notes,
    )

    return response
