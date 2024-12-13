from flask import request, jsonify
from app.blueprints.skills import skills_bp
from marshmallow import ValidationError
from app.models import Skill, db
from sqlalchemy import select
from app.blueprints.skills.schemas import skill_schema, skills_schema


@skills_bp.route("/", methods=["POST"])
def create_skill():
    try:
        skill_data = skill_schema.load(request.json)
        new_skill = Skill(name=skill_data["name"], description=skill_data.get("description"))
        db.session.add(new_skill)
        db.session.commit()
        return skill_schema.jsonify(new_skill), 201
    except ValidationError as e:
        return jsonify({"errors": e.messages}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@skills_bp.route("/", methods=["GET"])
def get_skills():
    query = select(Skill)
    skills = db.session.execute(query).scalars().all()
    return skills_schema.jsonify(skills), 200


