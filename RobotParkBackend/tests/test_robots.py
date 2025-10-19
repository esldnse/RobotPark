def test_create_robot_success(client):
    response = client.post('/robots', json={
        "name": "R2D2",
        "model": "Astromech",
        "type": "ground",
        "serial_number": "SN-001"
    })
    assert response.status_code == 201
    data = response.get_json()
    assert data['name'] == "R2D2"
    assert data['type'] == "ground"
    assert data['status'] == "idle"
    assert data['battery_level'] == 100


def test_create_robot_duplicate_name(client):
    client.post('/robots', json={
        "name": "R2D2",
        "model": "A",
        "type": "ground",
        "serial_number": "SN-001"
    })
    response = client.post('/robots', json={
        "name": "R2D2",  # то же имя
        "model": "B",
        "type": "aerial",
        "serial_number": "SN-002"
    })
    assert response.status_code == 400
    assert "error" in response.get_json()


def test_create_robot_duplicate_serial(client):
    client.post('/robots', json={
        "name": "R2D2",
        "model": "A",
        "type": "ground",
        "serial_number": "SN-001"
    })
    response = client.post('/robots', json={
        "name": "BB-8",
        "model": "Droid",
        "type": "ground",
        "serial_number": "SN-001"
    })
    assert response.status_code == 400
    assert "error" in response.get_json()


def test_create_robot_invalid_type(client):
    response = client.post('/robots', json={
        "name": "TestBot",
        "model": "X1",
        "type": "space",
        "serial_number": "SN-999"
    })
    assert response.status_code == 400
    assert "Invalid robot type" in response.get_json()["error"]


def test_create_robot_invalid_battery(client):
    response = client.post('/robots', json={
        "name": "TestBot",
        "model": "X1",
        "type": "ground",
        "serial_number": "SN-999",
        "battery_level": 150
    })
    assert response.status_code == 400
    assert "Battery must be between 0 and 100" in response.get_json()["error"]


def test_list_robots(client):
    client.post('/robots', json={
        "name": "R2D2", "model": "A", "type": "ground", "serial_number": "SN-001"
    })
    client.post('/robots', json={
        "name": "Drone-1", "model": "SkyX", "type": "aerial", "serial_number": "SN-002"
    })

    response = client.get('/robots')
    assert response.status_code == 200
    data = response.get_json()
    assert len(data) == 2


def test_list_robots_with_filters(client):
    client.post('/robots', json={
        "name": "R2D2", "model": "A", "type": "ground", "serial_number": "SN-001"
    })
    client.post('/robots', json={
        "name": "Drone-1", "model": "SkyX", "type": "aerial", "serial_number": "SN-002", "status": "busy"
    })

    response = client.get('/robots?type=ground')
    assert len(response.get_json()) == 1

    response = client.get('/robots?status=busy')
    assert len(response.get_json()) == 1

    response = client.get('/robots?type=aerial&status=busy')
    assert len(response.get_json()) == 1


def test_get_robot_by_id(client):
    resp = client.post('/robots', json={
        "name": "R2D2", "model": "A", "type": "ground", "serial_number": "SN-001"
    })
    robot_id = resp.get_json()['id']

    response = client.get(f'/robots/{robot_id}')
    assert response.status_code == 200
    assert response.get_json()['name'] == "R2D2"


def test_get_nonexistent_robot(client):
    response = client.get('/robots/999')
    assert response.status_code == 404


def test_update_robot(client):
    resp = client.post('/robots', json={
        "name": "R2D2", "model": "A", "type": "ground", "serial_number": "SN-001"
    })
    robot_id = resp.get_json()['id']

    response = client.patch(f'/robots/{robot_id}', json={
        "status": "busy",
        "battery_level": 75
    })
    assert response.status_code == 200
    data = response.get_json()
    assert data['status'] == "busy"
    assert data['battery_level'] == 75


def test_update_robot_invalid_status(client):
    resp = client.post('/robots', json={
        "name": "R2D2", "model": "A", "type": "ground", "serial_number": "SN-001"
    })
    robot_id = resp.get_json()['id']

    response = client.patch(f'/robots/{robot_id}', json={
        "status": "flying"
    })
    assert response.status_code == 400
    assert "Invalid robot status" in response.get_json()["error"]


def test_delete_robot_success(client):
    resp = client.post('/robots', json={
        "name": "R2D2", "model": "A", "type": "ground", "serial_number": "SN-001"
    })
    robot_id = resp.get_json()['id']

    response = client.delete(f'/robots/{robot_id}')
    assert response.status_code == 204

    response = client.get(f'/robots/{robot_id}')
    assert response.status_code == 404


def test_delete_robot_with_missions(client):
    robot_resp = client.post('/robots', json={
        "name": "R2D2", "model": "A", "type": "ground", "serial_number": "SN-001"
    })
    robot_id = robot_resp.get_json()['id']

    mt_resp = client.post('/mission_types', json={"name": "Inspect"})
    mt_id = mt_resp.get_json()['id']

    client.post('/missions', json={
        "robot_id": robot_id,
        "mission_type_id": mt_id,
        "title": "Test mission"
    })

    response = client.delete(f'/robots/{robot_id}')
    assert response.status_code == 409
    assert "error" in response.get_json()