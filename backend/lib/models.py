from __future__ import annotations
from typing import List
from sqlalchemy import String, ForeignKey, UniqueConstraint
from sqlalchemy.ext.asyncio import AsyncAttrs
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from datetime import datetime

# Sqlalchemy models for easy switching when moving from sqlite to something else
class Base(AsyncAttrs, DeclarativeBase):
    pass


class Link(Base):
    __tablename__ = "link"
    id: Mapped[int] = mapped_column(primary_key=True)
    location: Mapped[str] = mapped_column(String(100))
    link: Mapped[str] = mapped_column(String(200))
    job_id: Mapped[int] = mapped_column(ForeignKey("jobinfo.id"))

    job: Mapped["JobInfo"] = relationship(back_populates="links")


class JobInfo(Base):
    __tablename__ = "jobinfo"
    id: Mapped[int] = mapped_column(primary_key=True)
    company: Mapped[str] = mapped_column(String(100))
    job_name: Mapped[str] = mapped_column(String(100))
    applied: Mapped[bool] = mapped_column(default=False)
    last_attempted: Mapped[datetime | None] = mapped_column(nullable=True)

    links: Mapped[List[Link]] = relationship(back_populates="job", cascade="all, delete-orphan")

    __table_args__ = (
        UniqueConstraint("company", "job_name", name="uq_company_job"),
    )