from datetime import datetime
from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
  pass


class User(Base):
  __tablename__ = "users"

  id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
  username: Mapped[str] = mapped_column(
      String(50), unique=True, index=True, nullable=False
  )
  email: Mapped[str] = mapped_column(
      String(100), unique=True, index=True, nullable=False
  )
  hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
  role: Mapped[str] = mapped_column(
      String(20), default="user"
  )  # 'user', 'agent', 'admin'
  created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)

  # Relationships
  tickets_created: Mapped[list["Ticket"]] = relationship(
      "Ticket", foreign_keys="[Ticket.user_id]", back_populates="creator"
  )
  tickets_assigned: Mapped[list["Ticket"]] = relationship(
      "Ticket", foreign_keys="[Ticket.assigned_to_id]", back_populates="assignee"
  )


class Ticket(Base):
  __tablename__ = "tickets"

  id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
  title: Mapped[str] = mapped_column(String(150), nullable=False)
  description: Mapped[str] = mapped_column(Text, nullable=False)
  category: Mapped[str] = mapped_column(
      String(50), nullable=False
  )  # Network, Printer, Login, Software, Password
  priority: Mapped[str] = mapped_column(
      String(20), default="Medium"
  )  # Low, Medium, High, Critical
  status: Mapped[str] = mapped_column(
      String(20), default="Open"
  )  # Open, In Progress, Resolved, Closed

  # Foreign Keys
  user_id: Mapped[int] = mapped_column(
      Integer, ForeignKey("users.id"), nullable=False
  )
  assigned_to_id: Mapped[int | None] = mapped_column(
      Integer, ForeignKey("users.id"), nullable=True
  )

  # Timestamps & SLAs
  created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)
  updated_at: Mapped[datetime] = mapped_column(
      default=datetime.utcnow, onupdate=datetime.utcnow
  )
  sla_due_at: Mapped[datetime | None] = mapped_column(
      DateTime, nullable=True
  )  # For tracking SLA timers

  # Relationships mapping
  creator: Mapped["User"] = relationship(
      "User", foreign_keys=[user_id], back_populates="tickets_created"
  )
  assignee: Mapped["User | None"] = relationship(
      "User", foreign_keys=[assigned_to_id], back_populates="tickets_assigned"
  )