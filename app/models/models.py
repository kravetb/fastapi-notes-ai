from datetime import datetime

import sqlalchemy as sa
from sqlalchemy.orm import relationship

from app.database import Base


class NoteHistory(Base):
    __tablename__ = "note_histories"
    __table_args__ = (
        {
            "schema": "public",
        }
    )

    id = sa.Column(sa.Integer, primary_key=True, index=True)
    content = sa.Column(sa.Text)
    version = sa.Column(sa.Integer)
    updated_at = sa.Column(sa.DateTime, default=sa.func.now())
    note_id = sa.Column(
        sa.Integer,
        sa.ForeignKey("public.notes.id", ondelete="CASCADE")
    )

    note = relationship("Note", back_populates="histories")


class Note(Base):
    __tablename__ = "notes"
    __table_args__ = (
        {
            "schema": "public",
        }
    )

    id = sa.Column(sa.Integer, primary_key=True, index=True)
    title = sa.Column(sa.String, index=True)
    content = sa.Column(sa.Text)
    version = sa.Column(sa.Integer, default=1)

    histories = relationship("NoteHistory", back_populates="note")
