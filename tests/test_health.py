from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_home_endpoint():
    response = client.get("/")

    assert response.status_code == 200
    assert response.json() == {
        "message": "OpsPilot is running"
    }


def test_health_endpoint():
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {
        "status": "healthy",
        "service": "opspilot-api"
    }

def test_create_and_get_incident():
    incident_data = {
        "title": "Test payment failure",
        "description": "Payment API is failing during automated testing.",
        "severity": "high",
        "service_name": "payment-service",
    }

    create_response = client.post(
        "/incidents",
        json=incident_data
    )

    assert create_response.status_code == 200

    created_incident = create_response.json()

    assert created_incident["title"] == incident_data["title"]
    assert created_incident["status"] == "open"
    assert "id" in created_incident

    incident_id = created_incident["id"]

    get_response = client.get(
        f"/incidents/{incident_id}"
    )

    assert get_response.status_code == 200
    assert get_response.json()["id"] == incident_id

def test_create_and_get_incident_event():
    incident_data = {
        "title": "Test database issue",
        "description": "Database connection pool is exhausted.",
        "severity": "critical",
        "service_name": "database-service",
    }

    create_incident_response = client.post(
        "/incidents",
        json=incident_data
    )

    assert create_incident_response.status_code == 200

    incident_id = create_incident_response.json()["id"]

    event_data = {
        "message": "Investigation started.",
        "created_by": "test-user",
    }

    create_event_response = client.post(
        f"/incidents/{incident_id}/events",
        json=event_data
    )

    assert create_event_response.status_code == 200

    created_event = create_event_response.json()

    assert created_event["incident_id"] == incident_id
    assert created_event["message"] == event_data["message"]

    get_events_response = client.get(
        f"/incidents/{incident_id}/events"
    )

    assert get_events_response.status_code == 200

    events = get_events_response.json()

    assert len(events) >= 2

def test_receive_alert_creates_incident():
    alert_data = {
        "alert_name": "High CPU usage",
        "description": "CPU usage is above 90 percent.",
        "severity": "high",
        "service_name": "compute-service",
        "source": "prometheus",
    }

    response = client.post(
        "/alerts",
        json=alert_data
    )

    assert response.status_code == 200

    incident = response.json()

    assert incident["title"] == alert_data["alert_name"]
    assert incident["description"] == alert_data["description"]
    assert incident["severity"] == "high"
    assert incident["service_name"] == "compute-service"
    assert incident["status"] == "open"

    incident_id = incident["id"]

    events_response = client.get(
        f"/incidents/{incident_id}/events"
    )

    assert events_response.status_code == 200

    events = events_response.json()

    assert any(
        "prometheus" in event["message"]
        for event in events
    )

