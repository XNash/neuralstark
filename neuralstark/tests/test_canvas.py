import pytest
from fastapi.testclient import TestClient
from neuralstark.main import app

client = TestClient(app)

def test_save_and_get_canvas_template():
    template_id = "my_test_template"
    template_data = {"type": "bar_chart", "title": "My Test Template"}
    
    response = client.post("/canvas_templates", json={"template_id": template_id, "template_data": template_data})
    assert response.status_code == 200
    assert response.json() == {"message": f"Template '{template_id}' saved successfully."}
    
    response = client.get("/canvas_templates")
    assert response.status_code == 200
    templates = response.json()
    assert template_id in templates["user_templates"]
    assert templates["user_templates"][template_id] == template_data
