from __future__ import annotations

import json
from datetime import date, time

from sqlalchemy import Boolean, Date, ForeignKey, Integer, String, Text, Time, UniqueConstraint, select
from sqlalchemy.orm import Mapped, Session, mapped_column, relationship
from werkzeug.security import check_password_hash, generate_password_hash

from .database import Base


class User(Base):
    __tablename__ = "user"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    username: Mapped[str] = mapped_column(String(80), unique=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[str] = mapped_column(String(20), nullable=False, default="coach")

    def set_password(self, password: str) -> None:
        self.password_hash = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        return check_password_hash(self.password_hash, password)


class Position(Base):
    __tablename__ = "position"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    code: Mapped[str] = mapped_column(String(20), unique=True, nullable=False)
    label: Mapped[str] = mapped_column(String(120), nullable=False)


class PositionGroup(Base):
    __tablename__ = "position_group"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(80), unique=True, nullable=False)
    position_codes_json: Mapped[str] = mapped_column(Text, nullable=False, default="[]")

    @property
    def position_codes(self) -> list[str]:
        return json.loads(self.position_codes_json or "[]")

    @position_codes.setter
    def position_codes(self, value: list[str]) -> None:
        self.position_codes_json = json.dumps(value)


class TrainingTemplate(Base):
    __tablename__ = "training_template"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    valid_from: Mapped[date] = mapped_column(Date, nullable=False)
    valid_to: Mapped[date] = mapped_column(Date, nullable=False)
    weekday: Mapped[int] = mapped_column(Integer, nullable=False)
    start_time: Mapped[time] = mapped_column(Time, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)

    activities: Mapped[list["ActivityTemplate"]] = relationship(
        back_populates="training_template",
        cascade="all, delete-orphan",
        order_by="ActivityTemplate.order_index.asc()",
    )
    overrides: Mapped[list["TrainingOverride"]] = relationship(back_populates="training_template")


class ActivityTemplate(Base):
    __tablename__ = "activity_template"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    training_template_id: Mapped[int] = mapped_column(ForeignKey("training_template.id"), nullable=False)
    activity_type: Mapped[str] = mapped_column(String(40), nullable=False)
    duration_minutes: Mapped[int] = mapped_column(Integer, nullable=False)
    topic: Mapped[str | None] = mapped_column(String(255), nullable=True)
    order_index: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    position_codes_json: Mapped[str] = mapped_column(Text, nullable=False, default="[]")
    position_group_names_json: Mapped[str] = mapped_column(Text, nullable=False, default="[]")

    training_template: Mapped[TrainingTemplate] = relationship(back_populates="activities")

    @property
    def position_codes(self) -> list[str]:
        return json.loads(self.position_codes_json or "[]")

    @position_codes.setter
    def position_codes(self, value: list[str]) -> None:
        self.position_codes_json = json.dumps(value)

    @property
    def position_group_names(self) -> list[str]:
        return json.loads(self.position_group_names_json or "[]")

    @position_group_names.setter
    def position_group_names(self, value: list[str]) -> None:
        self.position_group_names_json = json.dumps(value)


class TrainingOverride(Base):
    __tablename__ = "training_override"
    __table_args__ = (UniqueConstraint("training_template_id", "date", name="uq_template_override_date"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    training_template_id: Mapped[int] = mapped_column(ForeignKey("training_template.id"), nullable=False)
    date: Mapped[date] = mapped_column(Date, nullable=False)
    cancelled: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    start_time: Mapped[time | None] = mapped_column(Time, nullable=True)
    activities_json: Mapped[str | None] = mapped_column(Text, nullable=True)

    training_template: Mapped[TrainingTemplate] = relationship(back_populates="overrides")


class AdHocTrainingInstance(Base):
    __tablename__ = "adhoc_training_instance"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    start_time: Mapped[time] = mapped_column(Time, nullable=False)
    activities_json: Mapped[str] = mapped_column(Text, nullable=False, default="[]")


def seed_default_positions(db: Session) -> None:
    defaults = ["OL", "DL", "LB", "RB", "DB", "TE", "WR", "QB"]
    existing = {row.code for row in db.scalars(select(Position)).all()}
    missing = [code for code in defaults if code not in existing]
    if not missing:
        return
    for code in missing:
        db.add(Position(code=code, label=code))
    db.commit()


def seed_default_users(db: Session, admin_username: str, admin_password: str, coach_username: str, coach_password: str) -> None:
    existing_count = db.query(User).count()
    if existing_count > 0:
        return

    admin = User(username=admin_username, role="admin")
    admin.set_password(admin_password)

    coach = User(username=coach_username, role="coach")
    coach.set_password(coach_password)

    db.add(admin)
    db.add(coach)
    db.commit()
