# app/models.py
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import ForeignKey, String, DateTime, JSON, Integer, Text
from datetime import datetime, timezone
from .db import Base

from pydantic import BaseModel, Field
from typing import List, Optional, Literal, Dict, Any

Role = Literal["user", "assistant", "system"]

class User(Base):
    __tablename__ = "users"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    sub: Mapped[str] = mapped_column(String(128), unique=True, index=True)  # Google subject
    email: Mapped[str] = mapped_column(String(256), unique=True, index=True)
    name: Mapped[str] = mapped_column(String(256), default="")
    picture: Mapped[str] = mapped_column(String(512), default="")

    google_account: Mapped[Optional["GoogleAccount"]] = relationship(back_populates="user", uselist=False)
    messages: Mapped[List["Message"]] = relationship(back_populates="user")
    meetings: Mapped[List["Meeting"]] = relationship(back_populates="user")
    emails: Mapped[List["Email"]] = relationship(back_populates="user")
    categories: Mapped[List["Category"]] = relationship(back_populates="user")

class GoogleAccount(Base):
    __tablename__ = "google_accounts"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    access_token: Mapped[str] = mapped_column(Text)
    refresh_token: Mapped[str] = mapped_column(Text)
    token_type: Mapped[str] = mapped_column(String(32))
    expires_at: Mapped[float] = mapped_column()  # epoch seconds
    scope: Mapped[str] = mapped_column(Text)
    raw_token: Mapped[Dict[str, Any]] = mapped_column(JSON)

    user: Mapped["User"] = relationship(back_populates="google_account")

class Message(Base):
    __tablename__ = "messages"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False, index=True)
    role: Mapped[str] = mapped_column(String(16), index=True)  # "user" | "assistant"
    content: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    user: Mapped["User"] = relationship(back_populates="messages")

class Meeting(Base):
    __tablename__ = "meetings"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False, index=True)
    title: Mapped[str] = mapped_column(String(255))
    start_iso: Mapped[str] = mapped_column(String(64))
    end_iso: Mapped[str] = mapped_column(String(64))
    attendees: Mapped[Dict[str, Any]] = mapped_column(JSON)  # {people: [{id,name,avatar?}]}

    user: Mapped["User"] = relationship(back_populates="meetings")

class Category(Base):
    __tablename__ = "categories"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(Text, default="")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    user: Mapped["User"] = relationship(back_populates="categories")
    emails: Mapped[List["Email"]] = relationship(back_populates="category")

class Email(Base):
    __tablename__ = "emails"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False, index=True)
    category_id: Mapped[Optional[int]] = mapped_column(ForeignKey("categories.id"), nullable=True, index=True)
    
    gmail_id: Mapped[str] = mapped_column(String(255), unique=True, index=True)  # Gmail message ID
    thread_id: Mapped[str] = mapped_column(String(255), index=True)
    subject: Mapped[str] = mapped_column(Text, default="")
    sender: Mapped[str] = mapped_column(String(512), default="")
    sender_email: Mapped[str] = mapped_column(String(512), default="")
    recipient: Mapped[str] = mapped_column(Text, default="")
    body_preview: Mapped[str] = mapped_column(Text, default="")
    received_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    labels: Mapped[List[str]] = mapped_column(JSON, default=list)
    is_read: Mapped[bool] = mapped_column(default=False)
    is_important: Mapped[bool] = mapped_column(default=False)
    
    user: Mapped["User"] = relationship(back_populates="emails")
    category: Mapped[Optional["Category"]] = relationship(back_populates="emails")

# Pydantic models (for API schemas)
class Person(BaseModel):
    id: str
    name: str
    avatar: Optional[str] = None

class MeetingOut(BaseModel):
    id: int
    title: str
    start_iso: str
    end_iso: str
    attendees: Dict[str, Any]  # { "people": Person[] }

class MeetingCreate(BaseModel):
    title: str
    start_iso: str   # ISO 8601 e.g. "2025-11-01T15:00:00Z"
    end_iso: str
    attendees: Dict[str, Any]  # { "people": [{ "id": "...", "name": "...", "avatar"?: "..." }] }

class MessageOut(BaseModel):
    id: int
    role: Role
    content: str
    created_at: datetime

class MessageIn(BaseModel):
    role: Role = Field("user")
    content: str

class ChatSendResponse(BaseModel):
    messages: List[MessageOut]
    meetings: List[MeetingOut]

class UserSummary(BaseModel):
    id: int
    email: str
    name: str
    sub: str
    created_meetings: int
    sent_messages: int
    has_google: bool

class GoogleAccountDetail(BaseModel):
    user_id: int
    user_email: str
    user_name: str
    scopes: str
    expires_at: datetime

class UserMessages(BaseModel):
    user_id: int
    user_email: str
    messages: List[Dict[str, Any]]

class UserMeetings(BaseModel):
    user_id: int
    user_email: str
    meetings: List[Dict[str, Any]]

class AdminStats(BaseModel):
    total_users: int
    total_messages: int
    total_meetings: int
    google_connected_users: int
    active_today: int

class CategoryOut(BaseModel):
    id: int
    name: str
    description: str
    email_count: int
    created_at: datetime

class EmailOut(BaseModel):
    id: int
    gmail_id: str
    subject: str
    sender: str
    sender_email: str
    body_preview: str
    received_at: datetime
    is_read: bool
    category_id: Optional[int] = None