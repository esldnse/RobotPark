from datetime import datetime
from app.schemas import RobotCreate, MissionCreate, MissionUpdate

def test_robot_create_valid():
    data = RobotCreate(
        name="R2D2",
        model="Astromech",
        type="ground",
        serial_number="SN-001"
    )
    assert data.name == "R2D2"
    assert data.type == "ground"
    assert data.status == "idle"
    assert data.battery_level == 100

def test_robot_create_invalid_type():
    try:
        RobotCreate(
            name="TestBot",
            model="X1",
            type="space",
            serial_number="SN-999"
        )
        assert False, "Должна быть ошибка валидации"
    except ValueError as e:
        assert "Invalid robot type" in str(e)

def test_mission_create_invalid_status():
    try:
        MissionCreate(
            robot_id=1,
            mission_type_id=1,
            title="Test",
            status="teleporting"  # недопустимый статус
        )
        assert False, "Должна быть ошибка валидации"
    except ValueError as e:
        assert "Invalid mission status" in str(e)

def test_mission_update_end_time_before_start():
    try:
        MissionUpdate(
            status="completed",
            start_time=datetime(2025, 10, 16, 10, 0, 0),
            end_time=datetime(2025, 10, 16, 9, 0, 0)  # раньше start_time
        )
        assert False, "Должна быть ошибка: end_time < start_time"
    except ValueError as e:
        assert "end_time must be >= start_time" in str(e)