import pytest
import json
from fastapi.testclient import TestClient
from neuralstark.main import app

client = TestClient(app)

def test_create_and_get_scheduled_report():
    report_name = "my_test_report"
    report_config = {
        "name": report_name,
        "tool_name": "FinancialReviewGenerator",
        "tool_input": {"company": "Test Corp"},
        "interval_minutes": 60
    }
    
    response = client.post("/scheduled_reports", json=report_config)
    assert response.status_code == 200
    assert response.json() == {"message": "Scheduled report created successfully."}
    
    response = client.get("/scheduled_reports")
    assert response.status_code == 200
    schedules = response.json()
    assert any(s["name"] == report_name for s in schedules)
