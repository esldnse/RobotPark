from pydantic import BaseModel, validator
from typing import Optional
from datetime import datetime

ROBOT_TYPES = {'ground', 'aerial', 'marine'}
ROBOT_STATUSES = {'idle', 'busy', 'maintenance', 'offline'}
MISSION_STATUSES = {'planned', 'in_progress', 'completed', 'failed', 'aborted'}

class RobotCreate(BaseModel):
    name: str
    model: str
    type: str
    serial_number: str
    status: Optional[str] = 'idle'
    battery_level: Optional[int] = 100

    @validator('type')
    def valid_type(cls, v):
        if v not in ROBOT_TYPES:
            raise ValueError('Invalid robot type')
        return v

    @validator('status')
    def valid_status(cls, v):
        if v not in ROBOT_STATUSES:
            raise ValueError('Invalid robot status')
        return v

    @validator('battery_level')
    def valid_battery(cls, v):
        if not (0 <= v <= 100):
            raise ValueError('Battery must be between 0 and 100')
        return v

class RobotUpdate(BaseModel):
    name: Optional[str] = None
    status: Optional[str] = None
    battery_level: Optional[int] = None

    @validator('status')
    def valid_status(cls, v):
        if v and v not in ROBOT_STATUSES:
            raise ValueError('Invalid robot status')
        return v

    @validator('battery_level')
    def valid_battery(cls, v):
        if v is not None and not (0 <= v <= 100):
            raise ValueError('Battery must be between 0 and 100')
        return v

class MissionTypeCreate(BaseModel):
    name: str

class MissionCreate(BaseModel):
    robot_id: int
    mission_type_id: int
    title: str
    status: Optional[str] = 'planned'
    start_time: Optional[datetime] = None

    @validator('status')
    def valid_status(cls, v):
        if v and v not in MISSION_STATUSES:
            raise ValueError('Invalid mission status')
        return v

class MissionUpdate(BaseModel):
    status: Optional[str] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    distance_meters: Optional[float] = None
    payload_kg: Optional[float] = None
    note: Optional[str] = None

    @validator('status')
    def valid_status(cls, v):
        if v and v not in MISSION_STATUSES:
            raise ValueError('Invalid mission status')
        return v

    @validator('distance_meters', 'payload_kg')
    def non_negative(cls, v):
        if v is not None and v < 0:
            raise ValueError('Value must be non-negative')
        return v

    @validator('end_time')
    def end_after_start(cls, v, values):
        start = values.get('start_time')
        if v and start and v < start:
            raise ValueError('end_time must be >= start_time')
        return v