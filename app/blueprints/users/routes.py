from flask import request, jsonify
from app.blueprints.users import users_bp
from app.blueprints.profile import profile_bp
from marshmallow import ValidationError
from app.models import User, db, Profile
from sqlalchemy import select
from app.blueprints.users.schemas import user_schema, users_schema, login_schema
from app.blueprints.profile.schemas import profile_schema
from werkzeug.security import check_password_hash, generate_password_hash
from app.models import User
from app.extensions import limiter
from app.utils.util import encode_token, token_required
from flask_cors import cross_origin

# Login schema //token

# @users_bp.route("/login", methods=["POST"])
# def login():
#     try:
#         creds = login_schema.load(request.json)
#     except ValidationError as e:
#         return jsonify(e.messages), 400
    
#     query = select(User).where(User.email == creds['email'])
#     user = db.session.execute(query).scalars().first()

#     if user and check_password_hash(user.password, creds['password']): 

#         token = encode_token(user.id)

#         response = {
#             "message": 'successfully logged in',
#             "status": "success",
#             "token": token
#         }

#         return jsonify(response), 200

#     return jsonify({"message": "Invalid credentials"}), 401

@users_bp.route("/login", methods=["POST"])
def login():
    try:
        creds = login_schema.load(request.json)
    except ValidationError as e:
        return jsonify(e.messages), 400
    
    query = select(User).where(User.email == creds['email'])
    user = db.session.execute(query).scalars().first()

    # Check if user exists and if the password matches
    if user and check_password_hash(user.password, creds['password']): 
        # User exists and password is correct
        response = {
            "message": "Successfully logged in",
            "status": "success",
            "user": {
                "id": user.id,
                "firstname": user.firstname,
                "lastname": user.lastname,
                "email": user.email
            }
        }
        return jsonify(response), 200

    # If the user is not found or password doesn't match
    return jsonify({"message": "Invalid credentials"}), 401


#===== Routes

@users_bp.route("/", methods=['POST'])
@cross_origin()
# # @limiter.limit("10 per hour")
def create_user():
    try:
        # Validate and deserialize input data
        user_data = user_schema.load(request.json)

        # checking for duplicate emails
        # existing_user = User.query.filter_by(email=user_data['email']).first()
        # if existing_user:
        #     return jsonify({"message": "User with this email already exists."}), 400

        # Hash the password before saving
        password_hash = generate_password_hash(user_data['password'])  # Hash the password

         # Create a new User instance with the hashed password
        new_user = User(
            firstname=user_data['firstname'],
            lastname=user_data['lastname'],
            email=user_data['email'],
            password=password_hash,  # Store the hashed password in the 'password' field
            rating=user_data.get('rating', 0)
        )

#         # Add user to the database
        db.session.add(new_user)
        db.session.commit()

        token = encode_token(new_user.id)

        return jsonify({
            "message": "User created successfully",
            "status": "success",
            "token": token  # Return token after successful sign-up
        }), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# sign up token
# @users_bp.route("/signup", methods=["POST"])
# def signup():
#     try:
#         user_data = request.json

#         # Check if the user already exists
#         existing_user = User.query.filter_by(email=user_data['email']).first()
#         if existing_user:
#             return jsonify({"message": "User with this email already exists."}), 400

#         # Hash the password before saving
#         password_hash = generate_password_hash(user_data['password'])

#         # Create a new User instance with the hashed password
#         new_user = User(
#             firstname=user_data['firstname'],
#             lastname=user_data['lastname'],
#             email=user_data['email'],
#             password=password_hash  # Store the hashed password in the 'password' field
#         )

#         # Add user to the database
#         db.session.add(new_user)
#         db.session.commit()

#         # Generate a token for the newly created user (optional, for instant login)
#         token = encode_token(new_user.id)  # Generate JWT token for the user

#         # Return the new user data and the token
#         return jsonify({
#             "message": "User created successfully",
#             "status": "success",
#             "token": token  # Send token so the user can be logged in immediately
#         }), 201

#     except Exception as e:
#         print(f"Error in signup: {str(e)}")
#         return jsonify({"error": str(e)}), 500

# @users_bp.route("/signup", methods=["POST"])
# def signup():
#     try:
#         # Deserialize and validate input data for user creation
#         user_data = user_schema.load(request.json)

#         # Check if the user already exists
#         existing_user = User.query.filter_by(email=user_data['email']).first()
#         if existing_user:
#             return jsonify({"message": "User with this email already exists."}), 400

#         # Hash the password before saving
#         password_hash = generate_password_hash(user_data['password'])

#         # Create a new User instance with the hashed password
#         new_user = User(
#             firstname=user_data['firstname'],
#             lastname=user_data['lastname'],
#             email=user_data['email'],
#             password=password_hash  # Store the hashed password in the 'password' field
#         )

#         # Add user to the database
#         db.session.add(new_user)
#         db.session.commit()

#         # Return success response
#         return jsonify({
#             "message": "User created successfully",
#             "status": "success"
#         }), 201

#     except ValidationError as e:
#         return jsonify({"errors": e.messages}), 400
#     except Exception as e:
#         print(f"Error in signup: {str(e)}")
#         return jsonify({"error": str(e)}), 500




@users_bp.route("/", methods=['OPTIONS'])
@cross_origin()
def handle_options():
    return "", 200  # Return a 200 OK status for the OPTIONS preflight request


@users_bp.route("/", methods=["GET"])
def get_users():
    query = select(User)
    users = db.session.execute(query).scalars().all()

    return users_schema.jsonify(users), 200

@users_bp.route("/<int:user_id>", methods=["GET"])
def get_user(user_id):
    user = db.session.get(User, user_id)

    return user_schema.jsonify(user), 200

@users_bp.route("/<int:user_id>", methods=["PUT"])
@token_required
def update_user(user_id):
    user = db.session.get(User, user_id)

    if user == None:
        return jsonify({"message": "invalid id"}), 400
    
    try:
        user_data = user_schema.load(request.json)
    except ValidationError as e:
        return jsonify(e.messages), 400
    
    for field, value in user_data.items():
        setattr(user, field, value)

    db.session.commit()
    return user_schema.jsonify(user), 200

@users_bp.route("/<int:user_id>", methods=["DELETE"])
@limiter.limit("1 per hour")
@token_required
def delete_user(user_id):
    user = db.session.get(User, user_id)

    if user == None:
        return jsonify({'messge': 'invalid id'}), 400
    
    db.session.delete(user)
    db.session.commit()
    return jsonify({'message': f"deleted user {user_id}!"})

# -------- PROFILE ----------------------

# profile TOKEN
# @users_bp.route("/profile", methods=["POST"])
# @token_required  # Ensure the user is logged in before accessing this route
# def create_or_update_profile():
#     try:

#         user_id = request.user_id
#         print(f"User ID from token: {user_id}")


#         # Get profile data from the request body
#         profile_data = request.json

#         # Get the user object using the user_id from the token
#         user = User.query.get(request.user_id)  # Access the user_id from the request object
#         if not user:
#             return jsonify({"error": "User not found"}), 404

#         # Check if a profile exists for the user, and create one if not
#         if user.profile is None:
#             # Create a new profile for the user
#             new_profile = Profile(
#                 user_id=user.id,
#                 bio=profile_data.get('bio'),
#                 avatar_url=profile_data.get('avatar_url'),
#                 location=profile_data.get('location'),
#                 contact_number=profile_data.get('contact_number')
#             )
#             db.session.add(new_profile)
#         else:
#             # Update the existing profile
#             user.profile.bio = profile_data.get('bio', user.profile.bio)
#             user.profile.avatar_url = profile_data.get('avatar_url', user.profile.avatar_url)
#             user.profile.location = profile_data.get('location', user.profile.location)
#             user.profile.contact_number = profile_data.get('contact_number', user.profile.contact_number)

#         # Commit the changes to the database
#         db.session.commit()

#         # Return the profile data in the response
#         return profile_schema.jsonify(user.profile), 200

#     except Exception as e:
#         return jsonify({"error": str(e)}), 500

@users_bp.route("/profile", methods=["POST"])
def create_or_update_profile():
    try:
        # Get profile data from the request body
        profile_data = request.json
        user_id = profile_data.get('user_id')  # User ID should be part of the profile data

        # Find the user by user_id
        user = User.query.get(user_id)
        if not user:
            return jsonify({"error": "User not found"}), 404

        # Check if a profile exists for the user
        if user.profile is None:
            # Create a new profile if none exists
            new_profile = Profile(
                user_id=user.id,
                bio=profile_data.get('bio'),
                avatar_url=profile_data.get('avatar_url'),
                location=profile_data.get('location'),
                contact_number=profile_data.get('contact_number')
            )
            db.session.add(new_profile)
        else:
            # Update the existing profile
            user.profile.bio = profile_data.get('bio', user.profile.bio)
            user.profile.avatar_url = profile_data.get('avatar_url', user.profile.avatar_url)
            user.profile.location = profile_data.get('location', user.profile.location)
            user.profile.contact_number = profile_data.get('contact_number', user.profile.contact_number)

        # Commit the changes to the database
        db.session.commit()

        # Return the profile data in the response using profile_schema
        return profile_schema.jsonify(user.profile), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500



@users_bp.route("/profile", methods=["DELETE"])
@token_required  # Ensure the user is logged in before accessing this route
def delete_profile(token_user):
    try:
        # Get the user object using the token_user (user_id)
        user = User.query.get(token_user)
        if not user or not user.profile:
            return jsonify({"error": "Profile not found"}), 404

        # Delete the profile
        db.session.delete(user.profile)
        db.session.commit()

        return jsonify({"message": "Profile deleted successfully"}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

    

@users_bp.route("/profile/delete", methods=["DELETE"])
@token_required  # Ensure the user is logged in before accessing this route
def delete_profile_fields(token_user):
    try:
        # Get the user object using the token_user (user_id)
        user = User.query.get(token_user)
        if not user or not user.profile:
            return jsonify({"error": "Profile not found"}), 404

        # Get which fields to delete from the request
        fields_to_delete = request.json.get('fields', [])

        # Delete the specified fields
        if 'bio' in fields_to_delete:
            user.profile.bio = None
        if 'avatar_url' in fields_to_delete:
            user.profile.avatar_url = None
        if 'location' in fields_to_delete:
            user.profile.location = None
        if 'contact_number' in fields_to_delete:
            user.profile.contact_number = None

        # Commit the changes to the database
        db.session.commit()

        return profile_schema.jsonify(user.profile), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

