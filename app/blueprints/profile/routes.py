from . import profile_bp
from flask import request, jsonify
from app.models import User, Profile, db
from app.utils.util import token_required
from app.blueprints.profile.schemas import profile_schema
from sqlalchemy.orm import Session
from sqlalchemy import select
from flask_cors import cross_origin

@profile_bp.route("/createprofile", methods=["POST"])
@token_required
def create_profile(current_user):
    try:
        profile_data = request.json

        user_id = current_user.id
        user_email = current_user.email

        # Check if the user already has a profile
        query = db.session.execute(
            select(Profile).filter_by(user_id=user_id)
        )
        existing_profile = query.scalars().first()

        if existing_profile:
            return jsonify({"message": "Profile already exists"}), 400

        # Create a new profile
        new_profile = Profile(
            user_id=current_user.id,
            full_name=profile_data.get('fullName'),
            email=current_user.email,
            phone=profile_data.get('phone'),
            mobile=profile_data.get('mobile'),
            address=profile_data.get('address'),
            avatar_url=profile_data.get('avatarUrl'),
            job_title=profile_data.get('jobTitle'),
            location=profile_data.get('location'),
            social_links=profile_data.get('socialLinks')
        )
        db.session.add(new_profile)
        db.session.commit()

        return jsonify({
            "message": "Profile created successfully",
            "profile": profile_schema.dump(new_profile)
        }), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500





@profile_bp.route("/", methods=["GET"])
@token_required
def get_profile(current_user):
    try:
        # Log current user information for debugging
        print(f"Current user: {current_user.id}, Email: {current_user.email}")

        # Query the user's profile
        profile = db.session.execute(
            select(Profile).filter_by(user_id=current_user.id)
        ).scalars().first()

        if not profile:
            return jsonify({"error": "Profile not found"}), 404

        return jsonify(profile_schema.dump(profile)), 200
    except Exception as e:
        print(f"Error in /profile/: {str(e)}")  # Log the error for debugging
        return jsonify({"error": "Internal Server Error"}), 500



# Delete Profile - Remove the profile for the logged-in user
@profile_bp.route("/", methods=["DELETE"])
@token_required
def delete_profile(current_user):
    try:
        # Check if the user has a profile
        if not current_user.profile:
            return jsonify({"error": "Profile not found"}), 404

        # Delete the profile
        db.session.delete(current_user.profile)
        db.session.commit()

        return jsonify({"message": "Profile deleted successfully"}), 200
    except Exception as e:
        return jsonify({"error": f"Failed to delete profile: {str(e)}"}), 500

# Delete specific profile fields (like bio, avatar, etc.)
@profile_bp.route("/delete", methods=["DELETE"])
@token_required
def delete_profile_fields(current_user):
    try:
        profile = current_user.profile
        if not profile:
            return jsonify({"error": "Profile not found"}), 404

        # Get which fields to delete from the request
        fields_to_delete = request.json.get('fields', [])

        # Dynamically set fields to None
        allowed_fields = ["bio", "avatar_url", "location", "contact_number"]
        for field in fields_to_delete:
            if field in allowed_fields:
                setattr(profile, field, None)

        # Commit the changes
        db.session.commit()

        return jsonify({"message": "Profile fields deleted successfully"}), 200
    except Exception as e:
        return jsonify({"error": f"Failed to delete profile fields: {str(e)}"}), 500

