from flask import Blueprint, request, jsonify
from app.extensions import db
from app.models import MissionType
from app.schemas import MissionTypeCreate
from pydantic import ValidationError

bp = Blueprint('mission_types', __name__)

@bp.route('', methods=['POST'])
def create_mission_type():
    try:
        data = MissionTypeCreate(**request.json)
    except ValidationError as e:
        return jsonify({"error": str(e)}), 400

    if MissionType.query.filter_by(name=data.name).first():
        return jsonify({"error": "Mission type name must be unique"}), 400

    mt = MissionType(**data.dict())
    db.session.add(mt)
    db.session.commit()
    return jsonify(mt.to_dict()), 201

@bp.route('', methods=['GET'])
def list_mission_types():
    types = MissionType.query.all()
    return jsonify([t.to_dict() for t in types])

@bp.route('/<int:id>', methods=['DELETE'])
def delete_mission_type(id):
    mt = MissionType.query.get_or_404(id)
    if mt.missions:
        return jsonify({"error": "Cannot delete mission type with missions"}), 409
    db.session.delete(mt)
    db.session.commit()
    return '', 204