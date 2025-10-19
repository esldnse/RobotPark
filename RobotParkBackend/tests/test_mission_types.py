def test_create_mission_type_success(client):
    resp = client.post('/mission_types', json={"name": "Inspection"})
    assert resp.status_code == 201
    assert resp.get_json()["name"] == "Inspection"

def test_create_mission_type_duplicate(client):
    client.post('/mission_types', json={"name": "Inspect"})
    resp = client.post('/mission_types', json={"name": "Inspect"})
    assert resp.status_code == 400
    assert "error" in resp.get_json()

def test_delete_mission_type_with_missions(client):
    mt = client.post('/mission_types', json={"name": "Inspect"}).get_json()
    r = client.post('/robots', json={"name": "R2D2", "model": "A", "type": "ground", "serial_number": "SN-001"}).get_json()
    client.post('/missions', json={"robot_id": r["id"], "mission_type_id": mt["id"], "title": "Test"})

    resp = client.delete(f'/mission_types/{mt["id"]}')
    assert resp.status_code == 409
    assert "error" in resp.get_json()