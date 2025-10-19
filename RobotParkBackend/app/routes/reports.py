from flask import Blueprint, request, jsonify
from datetime import datetime
from app.models import Mission
from app.extensions import db

bp = Blueprint('reports', __name__)

@bp.route('/monthly')
def monthly_report():
    try:
        year = int(request.args['year'])
        month = int(request.args['month'])
        if not (1 <= month <= 12):
            raise ValueError
    except (ValueError, KeyError):
        return jsonify({"error": "Invalid year/month"}), 400

    start = datetime(year, month, 1)
    if month == 12:
        end = datetime(year + 1, 1, 1)
    else:
        end = datetime(year, month + 1, 1)

    missions = Mission.query \
        .filter(Mission.start_time >= start) \
        .filter(Mission.start_time < end) \
        .join(Mission.robot) \
        .join(Mission.mission_type) \
        .all()

    try:
        total = len(missions)
        completed = len([m for m in missions if m.status == 'completed'])
        failed = len([m for m in missions if m.status == 'failed'])
        in_progress = len([m for m in missions if m.status == 'in_progress'])

        total_distance = sum(float(m.distance_meters or 0) for m in missions)

        mt_counts = {}
        for m in missions:
            key = m.mission_type.name
            if key not in mt_counts:
                mt_counts[key] = {'count': 0, 'distance_m': 0.0}
            mt_counts[key]['count'] += 1
            mt_counts[key]['distance_m'] += float(m.distance_meters or 0)

        by_mt = [{"mission_type": k, "count": v['count'], "distance_m": v['distance_m']} for k, v in mt_counts.items()]

        r_counts = {}
        for m in missions:
            key = m.robot.id
            name = m.robot.name
            if key not in r_counts:
                r_counts[key] = {'robot_name': name, 'count': 0, 'distance_m': 0.0}
            r_counts[key]['count'] += 1
            r_counts[key]['distance_m'] += float(m.distance_meters or 0)

        by_robot = [
            {"robot_id": k, "robot_name": v['robot_name'], "count": v['count'], "distance_m": v['distance_m']}
            for k, v in r_counts.items()
        ]

        result = {
            "month": f"{year}-{month:02d}",
            "total_missions": total,
            "completed": completed,
            "failed": failed,
            "in_progress": in_progress,
            "total_distance_m": total_distance,
            "by_mission_type": by_mt,
            "by_robot": by_robot
        }

        return jsonify(result)

    except Exception as e:
        return jsonify({"error": f"Internal error: {str(e)}"}), 500