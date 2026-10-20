from datetime import datetime

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from app.database import Base


class IncidentDB(Base):
    __tablename__ = "incidents"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=False)
    severity = Column(String(50), nullable=False)
    service_name = Column(String(100), nullable=False)
    status = Column(String(50), nullable=False, default="open")

    events = relationship(
        "IncidentEventDB",
        back_populates="incident",
        cascade="all, delete-orphan"
    )


class IncidentEventDB(Base):
    __tablename__ = "incident_events"

    id = Column(Integer, primary_key=True, index=True)
    incident_id = Column(
        Integer,
        ForeignKey("incidents.id"),
        nullable=False
    )
    message = Column(Text, nullable=False)
    created_by = Column(String(100), nullable=False)
    created_at = Column(
        DateTime,
        default=datetime.utcnow,
        nullable=False
    )

    incident = relationship(
        "IncidentDB",
        back_populates="events"
    )
