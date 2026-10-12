import json
import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

@pytest.fixture
def test_session_events(tmp_path, monkeypatch):
    test_log = tmp_path / "security_events.json"

    events = [
        {
            "timestamp": "2026-10-12T10:00:00",
            "attack_type": "SENSITIVE_FILE_ACCESS",
            "resource": "/files/finance/payroll.txt",
            "category": "finance",
            "filename": "payroll.txt",
            "session_id": "test_session_01",
            "source_ip": "127.0.0.1",
            "severity": "HIGH",
            "command": "GET /files/finance/payroll.txt"
        }
    ]

    test_log.write_text(json.dumps(events), encoding="utf-8")

    monkeypatch.setattr("app.main.LOG_FILE", test_log)

def test_security_summary_returns_success():
    response = client.get("/security/summary")

    assert response.status_code == 200

    data = response.json()
    assert data["status"] == "honeypot"
    assert "total_events" in data


def test_threat_analysis_returns_success(test_session_events):
    response = client.get("/threat/analyze/test_session_01")

    assert response.status_code == 200

    data = response.json()
    assert data["status"] == "honeypot"
    assert data["session_id"] == "test_session_01"
    assert "risk_score" in data
    assert 0 <= data["risk_score"] <= 100
    assert data["risk_level"] in [
        "LOW", "MEDIUM", "HIGH", "CRITICAL"
    ]


def test_threat_sequence_returns_success(test_session_events):
    response = client.get("/threat/sequence/test_session_01")

    assert response.status_code == 200

    data = response.json()
    assert data["status"] == "honeypot"
    assert data["session_id"] == "test_session_01"
    assert "total_events" in data
    assert "attack_sequence" in data
