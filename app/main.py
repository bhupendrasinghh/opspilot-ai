from datetime import datetime
from typing import List, Literal

from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, ConfigDict
from sqlalchemy.orm import Session

from app.database import Base, engine, get_db
from app.models import IncidentDB, IncidentEventDB


Base.metadata.create_all(bind=engine)


app = FastAPI(
    title="OpsPilot API",
    description="Enterprise AI operations platform",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)




class IncidentCreate(BaseModel):
    title: str
    description: str
    severity: Literal[
        "low",
        "medium",
        "high",
        "critical",
    ]
    service_name: str

class IncidentStatusUpdate(BaseModel):
    status: Literal[
        "open",
        "investigating",
        "resolved",
        "closed",
    ]

class AlertCreate(BaseModel):
    alert_name: str
    description: str
    severity: Literal[
        "low",
        "medium",
        "high",
        "critical",
    ]
    service_name: str
    source: str


class IncidentResponse(BaseModel):
    id: int
    title: str
    description: str
    severity: str
    service_name: str
    status: str

    model_config = ConfigDict(from_attributes=True)


class IncidentEventCreate(BaseModel):
    message: str
    created_by: str


class IncidentEventResponse(BaseModel):
    id: int
    incident_id: int
    message: str
    created_by: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


@app.get("/")
def home():
    return {
        "message": "OpsPilot is running"
    }


@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "service": "opspilot-api"
    }


@app.post("/incidents", response_model=IncidentResponse)
def create_incident(
    incident_data: IncidentCreate,
    db: Session = Depends(get_db)
):
    new_incident = IncidentDB(
        title=incident_data.title,
        description=incident_data.description,
        severity=incident_data.severity,
        service_name=incident_data.service_name,
        status="open",
    )

    db.add(new_incident)
    db.commit()
    db.refresh(new_incident)

    creation_event = IncidentEventDB(
        incident_id=new_incident.id,
        message="Incident created automatically.",
        created_by="system",
    )

    db.add(creation_event)
    db.commit()

    return new_incident

@app.get("/incidents", response_model=List[IncidentResponse])
def get_incidents(db: Session = Depends(get_db)):
    return db.query(IncidentDB).all()


@app.get(
    "/incidents/{incident_id}",
    response_model=IncidentResponse
)
def get_incident_by_id(
    incident_id: int,
    db: Session = Depends(get_db)
):
    incident = (
        db.query(IncidentDB)
        .filter(IncidentDB.id == incident_id)
        .first()
    )

    if incident is None:
        raise HTTPException(
            status_code=404,
            detail="Incident not found"
        )

    return incident


@app.patch(
    "/incidents/{incident_id}/status",
    response_model=IncidentResponse
)

@app.patch(
    "/incidents/{incident_id}/status",
    response_model=IncidentResponse
)
def update_incident_status(
    incident_id: int,
    status_data: IncidentStatusUpdate,
    db: Session = Depends(get_db)
):
    allowed_statuses = [
        "open",
        "investigating",
        "resolved",
        "closed",
    ]

    if status_data.status not in allowed_statuses:
        raise HTTPException(
            status_code=400,
            detail="Invalid status"
        )

    incident = (
        db.query(IncidentDB)
        .filter(IncidentDB.id == incident_id)
        .first()
    )

    if incident is None:
        raise HTTPException(
            status_code=404,
            detail="Incident not found"
        )

    old_status = incident.status
    incident.status = status_data.status

    status_event = IncidentEventDB(
        incident_id=incident.id,
        message=(
            f"Status changed from {old_status} "
            f"to {status_data.status}."
        ),
        created_by="system",
    )

    db.add(status_event)
    db.commit()
    db.refresh(incident)

    return incident

@app.post(
    "/incidents/{incident_id}/events",
    response_model=IncidentEventResponse
)
def create_incident_event(
    incident_id: int,
    event_data: IncidentEventCreate,
    db: Session = Depends(get_db)
):
    incident = (
        db.query(IncidentDB)
        .filter(IncidentDB.id == incident_id)
        .first()
    )

    if incident is None:
        raise HTTPException(
            status_code=404,
            detail="Incident not found"
        )

    new_event = IncidentEventDB(
        incident_id=incident_id,
        message=event_data.message,
        created_by=event_data.created_by,
    )

    db.add(new_event)
    db.commit()
    db.refresh(new_event)

    return new_event


@app.get(
    "/incidents/{incident_id}/events",
    response_model=List[IncidentEventResponse]
)
def get_incident_events(
    incident_id: int,
    db: Session = Depends(get_db)
):
    incident = (
        db.query(IncidentDB)
        .filter(IncidentDB.id == incident_id)
        .first()
    )

    if incident is None:
        raise HTTPException(
            status_code=404,
            detail="Incident not found"
        )

    return (
        db.query(IncidentEventDB)
        .filter(IncidentEventDB.incident_id == incident_id)
        .all()
    )

@app.post(
    "/alerts",
    response_model=IncidentResponse
)
def receive_alert(
    alert_data: AlertCreate,
    db: Session = Depends(get_db)
):
    new_incident = IncidentDB(
        title=alert_data.alert_name,
        description=alert_data.description,
        severity=alert_data.severity,
        service_name=alert_data.service_name,
        status="open",
    )

    db.add(new_incident)
    db.commit()
    db.refresh(new_incident)

    alert_event = IncidentEventDB(
        incident_id=new_incident.id,
        message=(
            f"Incident created from alert source: "
            f"{alert_data.source}"
        ),
        created_by="alert-system",
    )

    db.add(alert_event)
    db.commit()

    return new_incident
