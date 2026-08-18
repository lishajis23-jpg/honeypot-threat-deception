from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse
import json
from pathlib import Path
from datetime import datetime
from pydantic import BaseModel

BASE_DIR = Path(__file__).resolve().parent.parent
LOG_FILE = BASE_DIR / "logs" / "security_events.json"


def log_security_event(
    attack_type: str,
    resource: str,
    category: str,
    filename: str,
    session_id: str,
    source_ip: str,
    severity: str,
    command: str = ""
):
    event = {
        "timestamp": datetime.now().isoformat(),
        "attack_type": attack_type,
        "resource": resource,
        "category": category,
        "filename": filename,
        "session_id": session_id,
        "source_ip": source_ip,
        "severity": severity,
        "command": command
    }

    try:
        with open(LOG_FILE, "r", encoding="utf-8") as file:
            events = json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        events = []

    events.append(event)

    with open(LOG_FILE, "w", encoding="utf-8") as file:
        json.dump(events, file, indent=4)

app = FastAPI(
    title="Honeypot Threat Deception System",
    description="Fake enterprise environment for detecting and tracking suspicious activity",
    version="1.0.0"
)


# -----------------------------
# Load fake employee data
# -----------------------------

DATA_FILE = Path(__file__).parent.parent / "fake_data" / "employees.json"

with open(DATA_FILE, "r") as file:
    employees = json.load(file)


# -----------------------------
# Home endpoint
# -----------------------------

@app.get("/")
def home():
    return {
        "message": "Honeypot is running",
        "status": "active"
    }


# -----------------------------
# Get all employees
# -----------------------------

@app.get("/employees")
def get_employees():
    return {
        "count": len(employees),
        "employees": employees
    }

@app.get("/employees/search")
def search_employee(
    name: str = "",
    department: str = "",
    request: Request = None
):
    employees_file = BASE_DIR / "fake_data" / "employees.json"

    if not employees_file.exists():
        raise HTTPException(status_code=404, detail="Employee database not found")

    employees = json.loads(employees_file.read_text(encoding="utf-8"))

    results = []

    for employee in employees:
        if name and name.lower() not in employee["name"].lower():
            continue

        if department and department.lower() != employee["department"].lower():
            continue

        results.append(employee)

    log_security_event(
        attack_type="EMPLOYEE_DATABASE_SEARCH",
        resource="/employees/search",
        category="hr",
        filename="employees.json",
        session_id=request.headers.get("X-Session-ID", "anonymous"),
        source_ip=request.client.host if request.client else "unknown",
        severity="HIGH"
    )

    return {
        "status": "honeypot",
        "results_found": len(results),
        "employees": results
    }
# -----------------------------
# Get employee by ID
# -----------------------------

@app.get("/employees/{employee_id}")
def get_employee(employee_id: str):

    for employee in employees:

        if employee["employee_id"] == employee_id:
            return employee

    raise HTTPException(
        status_code=404,
        detail="Employee not found"
    )
    from pathlib import Path
from fastapi import HTTPException
from fastapi.responses import PlainTextResponse


BASE_DIR = Path(__file__).resolve().parent.parent
FAKE_FILES_DIR = BASE_DIR / "fake_data" / "files"


@app.get("/files/{category}/{filename}")
def access_fake_file(category: str, filename: str, request: Request):
    file_path = FAKE_FILES_DIR / category / filename

    # Security check: prevent path traversal
    try:
        file_path.resolve().relative_to(FAKE_FILES_DIR.resolve())
    except ValueError:
        raise HTTPException(status_code=403, detail="Access denied")

    if not file_path.exists() or not file_path.is_file():
        raise HTTPException(status_code=404, detail="File not found")

    content = file_path.read_text(encoding="utf-8")

    log_security_event(
    attack_type="SENSITIVE_FILE_ACCESS",
    resource=f"/files/{category}/{filename}",
    category=category,
    filename=filename,
    session_id=request.headers.get("X-Session-ID", "anonymous"),
    source_ip=request.client.host if request.client else "unknown",
    severity="HIGH",
    command=f"{request.method} /files/{category}/{filename}"
)

    return PlainTextResponse(
        content=content,
        headers={
            "X-Honeypot": "true",
            "X-Threat-Detection": "active"
        }
    )

    from pydantic import BaseModel


class LoginRequest(BaseModel):
    username: str
    password: str


@app.post("/admin/login")
def admin_login(data: LoginRequest, request: Request):

    log_security_event(
        attack_type="ADMIN_LOGIN_ATTEMPT",
        resource="/admin/login",
        category="admin",
        filename="login",
        session_id=request.headers.get("X-Session-ID", "anonymous"),
        source_ip=request.client.host if request.client else "unknown",
        severity="HIGH",
        command=f"POST /admin/login - username={data.username}"
    )

    return {
        "status": "access_denied",
        "message": "Invalid admin credentials"
    }
@app.post("/admin/escalate")
def privilege_escalation(request: Request):

    log_security_event(
        attack_type="PRIVILEGE_ESCALATION_ATTEMPT",
        resource="/admin/escalate",
        category="admin",
        filename="privilege",
        session_id=request.headers.get("X-Session-ID", "anonymous"),
        source_ip=request.client.host if request.client else "unknown",
        severity="CRITICAL",
        command="POST /admin/escalate"
    )

    return {
        "status": "honeypot",
        "message": "Privilege escalation attempt detected",
        "access": "denied"
    }
@app.get("/threat/sequence/{session_id}")
def get_attack_sequence(session_id: str):

    if not LOG_FILE.exists():
        raise HTTPException(
            status_code=404,
            detail="Security log file not found"
        )

    try:
        with open(LOG_FILE, "r", encoding="utf-8") as file:
            events = json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        events = []

    session_events = [
        event for event in events
        if event.get("session_id") == session_id
    ]

    if not session_events:
        raise HTTPException(
            status_code=404,
            detail="No events found for this session"
        )

    session_events.sort(
        key=lambda event: event.get("timestamp", "")
    )

    attack_sequence = []

    for index, event in enumerate(session_events, start=1):
        attack_sequence.append({
            "step": index,
            "attack_type": event.get("attack_type"),
            "resource": event.get("resource"),
            "category": event.get("category"),
            "severity": event.get("severity"),
            "timestamp": event.get("timestamp")
        })

    return {
        "status": "honeypot",
        "session_id": session_id,
        "total_events": len(attack_sequence),
        "attack_sequence": attack_sequence
    }
@app.get("/threat/analyze/{session_id}")
def analyze_threat(session_id: str):

    if not LOG_FILE.exists():
        raise HTTPException(
            status_code=404,
            detail="Security log file not found"
        )

    try:
        with open(LOG_FILE, "r", encoding="utf-8") as file:
            events = json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        events = []

    session_events = [
        event for event in events
        if event.get("session_id") == session_id
    ]

    if not session_events:
        raise HTTPException(
            status_code=404,
            detail="No events found for this session"
        )

    attack_types = [
        event.get("attack_type")
        for event in session_events
    ]

    resources = [
        event.get("resource")
        for event in session_events
    ]

    critical_events = [
        event for event in session_events
        if event.get("severity") == "CRITICAL"
    ]

    suspicious_reasons = []

    if len(session_events) >= 3:
        suspicious_reasons.append(
            "Multiple suspicious actions detected"
        )

    if critical_events:
        suspicious_reasons.append(
            "Critical security event detected"
        )

    if "PRIVILEGE_ESCALATION_ATTEMPT" in attack_types:
        suspicious_reasons.append(
            "Privilege escalation attempt detected"
        )

    if "SENSITIVE_FILE_ACCESS" in attack_types:
        suspicious_reasons.append(
            "Sensitive file access detected"
        )

    if "ADMIN_LOGIN_ATTEMPT" in attack_types:
        suspicious_reasons.append(
            "Administrative login attempt detected"
        )

    risk_level = "LOW"

    if critical_events or len(suspicious_reasons) >= 3:
        risk_level = "CRITICAL"
    elif len(suspicious_reasons) >= 2:
        risk_level = "HIGH"
    elif suspicious_reasons:
        risk_level = "MEDIUM"

    return {
        "status": "honeypot",
        "session_id": session_id,
        "risk_level": risk_level,
        "suspicious": len(suspicious_reasons) > 0,
        "events_count": len(session_events),
        "attack_types": attack_types,
        "resources_accessed": resources,
        "suspicious_behavior": suspicious_reasons
    }

@app.get("/security/summary")
def security_summary():
    try:
        with open(LOG_FILE, "r", encoding="utf-8") as file:
            events = json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        events = []

    total_events = len(events)

    severity_counts = {
        "CRITICAL": 0,
        "HIGH": 0,
        "MEDIUM": 0,
        "LOW": 0
    }

    attack_counts = {}
    sessions = set()

    for event in events:
        severity = event.get("severity", "LOW")
        if severity in severity_counts:
            severity_counts[severity] += 1

        attack_type = event.get("attack_type", "UNKNOWN")
        attack_counts[attack_type] = (
            attack_counts.get(attack_type, 0) + 1
        )

        sessions.add(
            event.get("session_id", "anonymous")
        )

    most_common_attack = None

    if attack_counts:
        most_common_attack = max(
            attack_counts,
            key=attack_counts.get
        )

    if severity_counts["CRITICAL"] > 0:
        current_threat = "CRITICAL"
    elif severity_counts["HIGH"] > 0:
        current_threat = "HIGH"
    elif severity_counts["MEDIUM"] > 0:
        current_threat = "MEDIUM"
    else:
        current_threat = "LOW"

    return {
        "status": "honeypot",
        "total_events": total_events,
        "critical_events": severity_counts["CRITICAL"],
        "high_events": severity_counts["HIGH"],
        "medium_events": severity_counts["MEDIUM"],
        "low_events": severity_counts["LOW"],
        "sessions_detected": len(sessions),
        "most_common_attack": most_common_attack,
        "current_threat": current_threat,
        "attack_counts": attack_counts
    }

class FakeDataModification(BaseModel):
    content: str


@app.put("/honeypot/data/{category}/{filename}")
def modify_fake_data(
    category: str,
    filename: str,
    data: FakeDataModification,
    request: Request
):
    file_path = FAKE_FILES_DIR / category / filename

    try:
        file_path.resolve().relative_to(FAKE_FILES_DIR.resolve())
    except ValueError:
        raise HTTPException(
            status_code=403,
            detail="Access denied"
        )

    if not file_path.exists() or not file_path.is_file():
        raise HTTPException(
            status_code=404,
            detail="Fake file not found"
        )

    file_path.write_text(
        data.content,
        encoding="utf-8"
    )

    session_id = request.headers.get(
        "X-Session-ID",
        "anonymous"
    )

    source_ip = (
        request.client.host
        if request.client
        else "unknown"
    )

    log_security_event(
        attack_type="FAKE_DATA_MODIFICATION",
        resource=f"/files/{category}/{filename}",
        category=category,
        filename=filename,
        session_id=session_id,
        source_ip=source_ip,
        severity="HIGH",
        command=f"PUT /honeypot/data/{category}/{filename}"
    )

    return {
        "status": "honeypot",
        "message": "Fake data modification detected",
        "resource": f"/files/{category}/{filename}",
        "action": "MODIFY",
        "access": "logged"
    }


@app.delete("/honeypot/data/{category}/{filename}")
def delete_fake_data(
    category: str,
    filename: str,
    request: Request
):
    file_path = FAKE_FILES_DIR / category / filename

    try:
        file_path.resolve().relative_to(FAKE_FILES_DIR.resolve())
    except ValueError:
        raise HTTPException(
            status_code=403,
            detail="Access denied"
        )

    if not file_path.exists() or not file_path.is_file():
        raise HTTPException(
            status_code=404,
            detail="Fake file not found"
        )

    session_id = request.headers.get(
        "X-Session-ID",
        "anonymous"
    )

    source_ip = (
        request.client.host
        if request.client
        else "unknown"
    )

    log_security_event(
        attack_type="FAKE_DATA_DELETION",
        resource=f"/files/{category}/{filename}",
        category=category,
        filename=filename,
        session_id=session_id,
        source_ip=source_ip,
        severity="CRITICAL",
        command=f"DELETE /honeypot/data/{category}/{filename}"
    )

    file_path.unlink()

    return {
        "status": "honeypot",
        "message": "Fake data deletion detected",
        "resource": f"/files/{category}/{filename}",
        "action": "DELETE",
        "access": "logged"
    }

@app.get("/dashboard", response_class=HTMLResponse)
def security_dashboard():
    return """
<!DOCTYPE html>
<html>
<head>
    <title>Honeypot Security Dashboard</title>

    <style>
        body {
            font-family: Arial, sans-serif;
            background: #111827;
            color: white;
            margin: 0;
            padding: 30px;
        }

        h1 {
            text-align: center;
            margin-bottom: 30px;
        }

        .status {
            text-align: center;
            margin-bottom: 25px;
            color: #22c55e;
            font-weight: bold;
        }

        .cards {
            display: grid;
            grid-template-columns: repeat(4, 1fr);
            gap: 20px;
            margin-bottom: 30px;
        }

        .card {
            background: #1f2937;
            padding: 25px;
            border-radius: 12px;
            text-align: center;
        }

        .card h2 {
            margin: 0;
            font-size: 32px;
        }

        .card p {
            color: #9ca3af;
            margin-bottom: 0;
        }

        .critical {
            color: #ef4444;
        }

        .high {
            color: #f97316;
        }

        .medium {
            color: #eab308;
        }

        .low {
            color: #22c55e;
        }

        .threat {
            color: #ef4444;
        }

        .panel {
            background: #1f2937;
            padding: 25px;
            border-radius: 12px;
            margin-bottom: 25px;
        }

        .attack {
            display: flex;
            justify-content: space-between;
            padding: 15px;
            border-bottom: 1px solid #374151;
        }

        .attack:last-child {
            border-bottom: none;
        }

        .attack-name {
            font-weight: bold;
        }

        .attack-count {
            color: #60a5fa;
            font-weight: bold;
        }

        button {
            display: block;
            margin: 20px auto;
            padding: 12px 25px;
            border: none;
            border-radius: 8px;
            background: #2563eb;
            color: white;
            cursor: pointer;
            font-size: 16px;
        }

        button:hover {
            background: #1d4ed8;
        }

        @media (max-width: 800px) {
            .cards {
                grid-template-columns: repeat(2, 1fr);
            }
        }
    </style>
</head>

<body>

    <h1>🛡️ Honeypot Security Monitoring Dashboard</h1>

    <div class="status">
        ● HONEYPOT SYSTEM ACTIVE
    </div>

    <div class="cards">

        <div class="card">
            <h2 id="total-events">-</h2>
            <p>Total Events</p>
        </div>

        <div class="card">
            <h2 id="critical" class="critical">-</h2>
            <p>Critical Events</p>
        </div>

        <div class="card">
            <h2 id="high" class="high">-</h2>
            <p>High Events</p>
        </div>

        <div class="card">
            <h2 id="sessions">-</h2>
            <p>Sessions Detected</p>
        </div>

    </div>

    <div class="panel">

        <h2>Current Threat Level</h2>

        <h1 id="threat" class="threat">
            Loading...
        </h1>

        <p>
            Most Common Attack:
            <strong id="common-attack">Loading...</strong>
        </p>

    </div>

    <div class="panel">

        <h2>Attack Types</h2>

        <div id="attack-list">
            Loading...
        </div>

    </div>

    
<div class="panel">
    <h2>Attack Timeline</h2>

    <div id="attack-timeline">
        Loading attack timeline...
    </div>

</div>
<button onclick="loadDashboard()">
        🔄 Refresh Dashboard
</button>

<script>

async function loadDashboard() {

    try {

        const response = await fetch("/security/summary");

        const data = await response.json();

        document.getElementById("total-events").textContent =
            data.total_events;

        document.getElementById("critical").textContent =
            data.critical_events;

        document.getElementById("high").textContent =
            data.high_events;

        document.getElementById("sessions").textContent =
            data.sessions_detected;

        document.getElementById("threat").textContent =
            data.current_threat;

        document.getElementById("common-attack").textContent =
            data.most_common_attack || "None";

        const attackList =
            document.getElementById("attack-list");

        attackList.innerHTML = "";

        for (const [attack, count]
             of Object.entries(data.attack_counts)) {

            const div = document.createElement("div");

            div.className = "attack";

            div.innerHTML = `
                <span class="attack-name">
                    ${attack}
                </span>

                <span class="attack-count">
                    ${count}
                </span>
            `;

            attackList.appendChild(div);
        }
        // Load attack timeline separately
try {
    const timelineResponse = await fetch(
        "/threat/sequence/anonymous"
    );

    const timelineData = await timelineResponse.json();

    const timeline = document.getElementById("attack-timeline");

    timeline.innerHTML = "";

    if (timelineData.attack_sequence) {
        timelineData.attack_sequence.forEach(event => {

            const div = document.createElement("div");

            div.className = "attack";

            div.innerHTML = `
                <strong>Step ${event.step} — ${event.attack_type}</strong>
                <br>
                Resource: ${event.resource}
                <br>
                Severity: ${event.severity}
            `;

            timeline.appendChild(div);
        });
    }

} catch (timelineError) {

    console.error("Timeline error:", timelineError);

}
                

    } catch (error) {

                const timeline = document.getElementById("attack-timeline");

        try {
            const sequenceResponse =
                await fetch("/threat/sequence/anonymous");

            const sequenceData =
                await sequenceResponse.json();

            timeline.innerHTML = "";

            sequenceData.attack_sequence.forEach((event, index) => {

                const item = document.createElement("div");

                item.style.padding = "12px";
                item.style.marginBottom = "8px";
                item.style.borderLeft = "4px solid #ff4d4d";
                item.style.background = "#182233";
                item.style.borderRadius = "6px";

                item.innerHTML = `
                    <strong>Step ${index + 1}</strong>
                    — ${event.attack_type}
                    <br>
                    <small>
                        Resource: ${event.resource}
                    </small>
                    <br>
                    <small>
                        Severity: ${event.severity}
                    </small>
                `;

                timeline.appendChild(item);
            });

        } catch (error) {

            timeline.textContent =
                "Unable to load attack timeline.";

            console.error(error);
        }

        document.getElementById("threat").textContent =
            "ERROR";

        console.error(error);
    }
}

loadDashboard();

</script>

</body>
</html>
"""