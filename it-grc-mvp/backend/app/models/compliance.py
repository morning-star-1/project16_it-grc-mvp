from sqlalchemy import Integer, String, Text, ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base

class Framework(Base):
    __tablename__ = "frameworks"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(120), unique=True, index=True)

class Control(Base):
    __tablename__ = "controls"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(180), unique=True, index=True)
    description: Mapped[str] = mapped_column(Text, default="")

class ControlMapping(Base):
    __tablename__ = "control_mappings"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)

    control_id: Mapped[int] = mapped_column(ForeignKey("controls.id", ondelete="CASCADE"))
    framework_id: Mapped[int] = mapped_column(ForeignKey("frameworks.id", ondelete="CASCADE"))

    status: Mapped[str] = mapped_column(String(30), default="PARTIAL")  # COMPLIANT/PARTIAL/NONCOMPLIANT
    notes: Mapped[str] = mapped_column(Text, default="")

    control = relationship("Control")
    framework = relationship("Framework")

    __table_args__ = (UniqueConstraint("control_id", "framework_id", name="uq_control_framework"),)
