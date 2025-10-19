from app.extensions import db
from sqlalchemy import CheckConstraint, ForeignKey
from sqlalchemy.orm import validates

class Robot(db.Model):
    __tablename__ = 'robots'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    model = db.Column(db.String(100), nullable=False)
    type = db.Column(db.String(20), nullable=False)
    serial_number = db.Column(db.String(100), unique=True, nullable=False)
    status = db.Column(db.String(20), default='idle')
    battery_level = db.Column(db.Integer, default=100)

    __table_args__ = (
        CheckConstraint(status.in_(['idle', 'busy', 'maintenance', 'offline'])),
        CheckConstraint(battery_level.between(0, 100)),
        CheckConstraint(type.in_(['ground', 'aerial', 'marine'])),
    )

    missions = db.relationship('Mission', back_populates='robot', cascade='all, delete-orphan')

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'model': self.model,
            'type': self.type,
            'serial_number': self.serial_number,
            'status': self.status,
            'battery_level': self.battery_level
        }

class MissionType(db.Model):
    __tablename__ = 'mission_types'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)

    missions = db.relationship('Mission', back_populates='mission_type', cascade='all, delete-orphan')

    def to_dict(self):
        return {'id': self.id, 'name': self.name}

class Mission(db.Model):
    __tablename__ = 'missions'

    id = db.Column(db.Integer, primary_key=True)
    robot_id = db.Column(db.Integer, ForeignKey('robots.id'), nullable=False)
    mission_type_id = db.Column(db.Integer, ForeignKey('mission_types.id'), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    status = db.Column(db.String(20), default='planned')
    start_time = db.Column(db.DateTime, nullable=True)
    end_time = db.Column(db.DateTime, nullable=True)
    distance_meters = db.Column(db.Numeric(precision=10, scale=2), nullable=True)
    payload_kg = db.Column(db.Numeric(precision=10, scale=2), nullable=True)
    note = db.Column(db.Text, nullable=True)

    __table_args__ = (
        CheckConstraint(status.in_(['planned', 'in_progress', 'completed', 'failed', 'aborted'])),
    )

    robot = db.relationship('Robot', back_populates='missions')
    mission_type = db.relationship('MissionType', back_populates='missions')

    @validates('end_time')
    def validate_end_time(self, key, end_time):
        if end_time and self.start_time and end_time < self.start_time:
            raise ValueError("end_time must be >= start_time")
        return end_time

    def to_dict(self):
        return {
            'id': self.id,
            'robot_id': self.robot_id,
            'mission_type_id': self.mission_type_id,
            'title': self.title,
            'status': self.status,
            'start_time': self.start_time.isoformat() if self.start_time else None,
            'end_time': self.end_time.isoformat() if self.end_time else None,
            'distance_meters': float(self.distance_meters) if self.distance_meters else None,
            'payload_kg': float(self.payload_kg) if self.payload_kg else None,
            'note': self.note
        }