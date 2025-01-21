from . import profile_bp
from flask import request, jsonify
from app.models import User, Profile, db, Skill, user_skills
from app.utils.util import token_required
from app.blueprints.profile.schemas import profile_schema
from sqlalchemy.orm import Session
from sqlalchemy import select
from flask_cors import cross_origin
import requests
import os
import base64

UPLOAD_FOLDER = os.path.join("static", "profile-images")
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@profile_bp.route("/users/<int:user_id>/skills", methods=["GET"])
@token_required
def get_user_skills(current_user, user_id):
    if current_user.id != user_id and current_user.role != 'admin':
        return jsonify({"error": "Unauthorized"}), 403

    user = db.session.execute(select(User).filter_by(id=user_id)).scalars().first()
    if not user:
        return jsonify({"error": "User not found"}), 404

    skills = [{"id": skill.id, "name": skill.name, "description": skill.description} for skill in user.skills]

    return jsonify({"user_id": user.id, "skills": skills}), 200


@profile_bp.route("/createprofile", methods=["POST"])
@token_required
def create_profile(current_user):
    try:
        profile_data = request.json or {}
        user_id = current_user.id

        # Check if the user already has a profile MOVED TO THE BOTTOM
        # query = db.session.execute(
        #     select(Profile).filter_by(user_id=user_id)
        # )
        # existing_profile = query.scalars().first()

        # if existing_profile:
        #     return jsonify({"message": "Profile already exists"}), 400
        
        zip_code = profile_data.get('zip_code')
        if not zip_code:
            return jsonify({"error": "ZIP code is required"}), 400
        
        response = requests.get(f"http://api.zippopotam.us/us/{zip_code}")
        if response.status_code != 200:
            return jsonify({"error": "Invalid ZIP code"}), 400

        location_data = response.json()
        city = location_data["places"][0]["place name"]
        state = location_data["places"][0]["state"]

        # Check if the user already has a profile
        query = db.session.execute(
            select(Profile).filter_by(user_id=user_id)
        )
        existing_profile = query.scalars().first()

        if existing_profile:
            return jsonify({"message": "Profile already exists"}), 400

        # Handle optional profile picture
        profile_picture_data = profile_data.get('profile_picture')
        if profile_picture_data:
            # Decode the base64 string and save it as a file
            try:
                file_data = base64.b64decode(profile_picture_data.split(",")[1])  # Remove "data:image/*;base64,"
                filename = f"{user_id}_profile_picture.png"
                file_path = os.path.join(UPLOAD_FOLDER, filename)
                with open(file_path, "wb") as f:
                    f.write(file_data)
                profile_picture_path = f"/{UPLOAD_FOLDER}/{filename}"

            except Exception as e:
                return jsonify({"error": f"Failed to process profile picture: {str(e)}"}), 400
        else:
            profile_picture_path = "static/profile-images/default-profile.png"  # Default picture

        # Combine first and last name if separate fields are present
        first_name = profile_data.get('firstName', "").strip()
        last_name = profile_data.get('lastName', "").strip()
        full_name = f"{first_name} {last_name}".strip() if first_name or last_name else None


        skill_ids = profile_data.get('skill_ids', [])
        skills = []
        if skill_ids:
            skills_query = db.session.execute(
                select(Skill).filter(Skill.id.in_(skill_ids))
            )
            skills = skills_query.scalars().all()

            if len(skills) != len(skill_ids):
                return jsonify({"error": "One or more skill IDs are invalid"}), 400
            
            current_user.skills = skills

        # Create a new profile
        new_profile = Profile(
            user_id=current_user.id,
            full_name=full_name,
            email=current_user.email,
            phone=profile_data.get('phone'),
            city=city,  # Add city
            state=state,  # Add state
            zip_code=zip_code,  # Add zip_code
            profile_picture=profile_picture_path,
            social_links=profile_data.get('social_links'),
            account_type=profile_data.get('account_type', 'regular'),
            bio=profile_data.get('bio'),
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
        # Query the user's profile
        profile = db.session.execute(
            select(Profile).filter_by(user_id=current_user.id)
        ).scalars().first()

        if not profile:
            return jsonify({"error": "Profile not found"}), 404

        # Manually add full_name by combining first and last name
        profile_data = profile_schema.dump(profile)
        profile_data['full_name'] = f"{current_user.firstname} {current_user.lastname}"

        skills = [skill.name for skill in current_user.skills]
        job_title = skills[0] if skills else "N/A"

        # Map backend field names to frontend field names
        response_data = {
            "fullName": profile_data["full_name"],
            "email": profile.email,
            "phone": profile.phone,
            "avatarUrl": profile.profile_picture,
            "jobTitle": job_title,
            "city": profile.city,         # Updated field
            "state": profile.state,       # Updated field
            "zipCode": profile.zip_code,  # Updated field
            "socialLinks": profile.social_links or {
                "github": "",
                "twitter": "",
                "instagram": "",
                "facebook": ""
            },
            "bio": profile.bio,  # Include bio for additional display
            "skills": skills,
        }

        return jsonify(response_data), 200
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

