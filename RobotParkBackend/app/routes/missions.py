from flask import Blueprint, request, jsonify
from app.extensions import db
from app.models import Mission, Robot, MissionType
from app.schemas import MissionCreate, MissionUpdate
from pydantic import ValidationError
from datetime import datetime

bp = Blueprint('missions', __name__)

@bp.route('', methods=['POST'])
def create_mission():
    try:
        data = MissionCreate(**request.json)
    except ValidationError as e:
        return jsonify({"error": str(e)}), 400

    if not Robot.query.get(data.robot_id):
        return jsonify({"error": "Robot not found"}), 404
    if not MissionType.query.get(data.mission_type_id):
        return jsonify({"error": "Mission type not found"}), 404

    mission = Mission(**data.dict())
    db.session.add(mission)
    db.session.commit()
    return jsonify(mission.to_dict()), 201

@bp.route('', methods=['GET'])
def list_missions():
    query = Mission.query

    robot_id = request.args.get('robot_id', type=int)
    if robot_id:
        query = query.filter_by(robot_id=robot_id)

    mission_type_id = request.args.get('mission_type_id', type=int)
    if mission_type_id:
        query = query.filter_by(mission_type_id=mission_type_id)

    status = request.args.get('status')
    if status:
        query = query.filter_by(status=status)

    date_from = request.args.get('date_from')
    date_to = request.args.get('date_to')

    if date_from:
        try:
            dt_from = datetime.fromisoformat(date_from)
            query = query.filter(Mission.start_time >= dt_from)
        except ValueError:
            return jsonify({"error": "Invalid date_from format"}), 400
    if date_to:
        try:
            dt_to = datetime.fromisoformat(date_to)
            query = query.filter(Mission.start_time <= dt_to)
        except ValueError:
            return jsonify({"error": "Invalid date_to format"}), 400

    missions = query.all()
    return jsonify([m.to_dict() for m in missions])

@bp.route('/<int:id>', methods=['GET'])
def get_mission(id):
    mission = Mission.query.get_or_404(id)
    return jsonify(mission.to_dict())

@bp.route('/<int:id>', methods=['PATCH'])
def update_mission(id):
    mission = Mission.query.get_or_404(id)
    try:
        data = MissionUpdate(**request.json)
    except ValidationError as e:
        return jsonify({"error": str(e)}), 400

    for key, value in data.dict(exclude_unset=True).items():
        if value is not None:
            try:
                setattr(mission, key, value)
            except ValueError as e:
                return jsonify({"error": str(e)}), 400
    db.session.commit()
    return jsonify(mission.to_dict())

@bp.route('/<int:id>', methods=['DELETE'])
def delete_mission(id):
    mission = Mission.query.get_or_404(id)
    db.session.delete(mission)
    db.session.commit()
    return '', 204