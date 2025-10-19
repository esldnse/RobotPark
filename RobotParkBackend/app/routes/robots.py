from flask import Blueprint, request, jsonify
from app.extensions import db
from app.models import Robot
from app.schemas import RobotCreate, RobotUpdate
from pydantic import ValidationError

bp = Blueprint('robots', __name__)

@bp.route('', methods=['POST'])
def create_robot():
    try:
        data = RobotCreate(**request.json)
    except ValidationError as e:
        return jsonify({"error": str(e)}), 400

    if Robot.query.filter_by(name=data.name).first():
        return jsonify({"error": "Robot name must be unique"}), 400
    if Robot.query.filter_by(serial_number=data.serial_number).first():
        return jsonify({"error": "Serial number must be unique"}), 400

    robot = Robot(**data.dict())
    db.session.add(robot)
    db.session.commit()
    return jsonify(robot.to_dict()), 201

@bp.route('', methods=['GET'])
def list_robots():
    robot_type = request.args.get('type')
    status = request.args.get('status')
    query = Robot.query
    if robot_type:
        query = query.filter_by(type=robot_type)
    if status:
        query = query.filter_by(status=status)
    robots = query.all()
    return jsonify([r.to_dict() for r in robots])

@bp.route('/<int:id>', methods=['GET'])
def get_robot(id):
    robot = Robot.query.get_or_404(id)
    return jsonify(robot.to_dict())

@bp.route('/<int:id>', methods=['PATCH'])
def update_robot(id):
    robot = Robot.query.get_or_404(id)
    try:
        data = RobotUpdate(**request.json)
    except ValidationError as e:
        return jsonify({"error": str(e)}), 400

    for key, value in data.dict(exclude_unset=True).items():
        if value is not None:
            setattr(robot, key, value)
    db.session.commit()
    return jsonify(robot.to_dict())

@bp.route('/<int:id>', methods=['DELETE'])
def delete_robot(id):
    robot = Robot.query.get_or_404(id)
    if robot.missions:
        return jsonify({"error": "Cannot delete robot with missions"}), 409
    db.session.delete(robot)
    db.session.commit()
    return '', 204