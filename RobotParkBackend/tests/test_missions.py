def test_create_mission_success(client):
    r = client.post('/robots', json={"name": "R2D2", "model": "A", "type": "ground", "serial_number": "SN-001"}).get_json()
    mt = client.post('/mission_types', json={"name": "Inspect"}).get_json()

    resp = client.post('/missions', json={
        "robot_id": r["id"],
        "mission_type_id": mt["id"],
        "title": "Inspect corridor A",
        "start_time": "2025-10-16T09:00:00"
    })
    assert resp.status_code == 201
    data = resp.get_json()
    assert data["title"] == "Inspect corridor A"
    assert data["status"] == "planned"

def test_create_mission_nonexistent_robot(client):
    mt = client.post('/mission_types', json={"name": "Inspect"}).get_json()
    resp = client.post('/missions', json={
        "robot_id": 999,
        "mission_type_id": mt["id"],
        "title": "Test"
    })
    assert resp.status_code == 404
    assert "error" in resp.get_json()

def test_create_mission_nonexistent_type(client):
    r = client.post('/robots', json={"name": "R2D2", "model": "A", "type": "ground", "serial_number": "SN-001"}).get_json()
    resp = client.post('/missions', json={
        "robot_id": r["id"],
        "mission_type_id": 999,
        "title": "Test"
    })
    assert resp.status_code == 404
    assert "error" in resp.get_json()

def test_list_missions_with_filters(client):
    r = client.post('/robots', json={"name": "R2D2", "model": "A", "type": "ground", "serial_number": "SN-001"}).get_json()
    mt = client.post('/mission_types', json={"name": "Inspect"}).get_json()

    client.post('/missions', json={"robot_id": r["id"], "mission_type_id": mt["id"], "title": "M1", "status": "completed", "start_time": "2025-10-19T10:00:00"})
    client.post('/missions', json={"robot_id": r["id"], "mission_type_id": mt["id"], "title": "M2", "status": "failed", "start_time": "2025-10-19T11:00:00"})

    resp = client.get('/missions?status=completed')
    assert resp.status_code == 200
    data = resp.get_json()
    assert len(data) == 1
    assert data[0]["status"] == "completed"

def test_update_mission_end_time_before_start(client):
    r = client.post('/robots', json={"name": "R2D2", "model": "A", "type": "ground", "serial_number": "SN-001"}).get_json()
    mt = client.post('/mission_types', json={"name": "Inspect"}).get_json()
    m = client.post('/missions', json={
        "robot_id": r["id"],
        "mission_type_id": mt["id"],
        "title": "Test",
        "start_time": "2025-10-16T10:00:00"
    }).get_json()

    resp = client.patch(f'/missions/{m["id"]}', json={
        "end_time": "2025-10-16T09:00:00"  # раньше start_time
    })
    assert resp.status_code == 400
    assert "end_time must be >= start_time" in resp.get_json()["error"]

def test_update_mission_negative_distance(client):
    r = client.post('/robots', json={"name": "R2D2", "model": "A", "type": "ground", "serial_number": "SN-001"}).get_json()
    mt = client.post('/mission_types', json={"name": "Inspect"}).get_json()
    m = client.post('/missions', json={"robot_id": r["id"], "mission_type_id": mt["id"], "title": "Test"}).get_json()

    resp = client.patch(f'/missions/{m["id"]}', json={"distance_meters": -10})
    assert resp.status_code == 400
    assert "Value must be non-negative" in resp.get_json()["error"]