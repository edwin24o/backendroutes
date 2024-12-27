from flask import jsonify, request
from app.models import db, User
from app.blueprints.profile.schemas import profile_schema
from app.extensions import limiter
from app.utils.util import token_required
from marshmallow import ValidationError
from . import profile_bp

@profile_bp.route("/<int:user_id>", methods=["GET"])
@token_required
def get_profile(user_id):
    """Retrieve a user's profile by ID."""
    user = db.session.get(User, user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404
    return profile_schema.jsonify(user), 200


@profile_bp.route("/<int:user_id>", methods=["PUT"])
@token_required
def update_profile(user_id):
    """Update the profile of a user."""
    user = db.session.get(User, user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404

    try:
        # Validate and deserialize request data
        profile_data = profile_schema.load(request.json)
    except ValidationError as e:
        return jsonify({"errors": e.messages}), 400

    # Update user fields
    for field, value in profile_data.items():
        setattr(user, field, value)

    db.session.commit()
    return profile_schema.jsonify(user), 200


@profile_bp.route("/<int:user_id>", methods=["DELETE"])
@limiter.limit("1 per hour")
@token_required
def delete_profile(user_id):
    """Delete a user's profile."""
    user = db.session.get(User, user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404

    db.session.delete(user)
    db.session.commit()
    return jsonify({"message": f"User {user_id} deleted successfully!"}), 200


