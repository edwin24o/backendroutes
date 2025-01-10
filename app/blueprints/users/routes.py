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

@users_bp.route("/login", methods=["POST"])
def login():
    try:
        creds = login_schema.load(request.json)
    except ValidationError as e:
        return jsonify(e.messages), 400
    
    query = select(User).where(User.email == creds['email'])
    user = db.session.execute(query).scalars().first()

    if user and check_password_hash(user.password, creds['password']): 

        token = encode_token(user.id)

        has_profile = user.profile is not None

        response = {
            "message": 'successfully logged in',
            "status": "success",
            "token": token,
            "user": {
                "id": user.id,
                "firstname": user.firstname,
                "lastname": user.lastname,
                "email": user.email,
                "hasProfile": has_profile  # Include hasProfile in the response
            }
        }

        return jsonify(response), 200

    return jsonify({"message": "Invalid credentials"}), 401

    
@users_bp.route("/", methods=['POST'])
@cross_origin()
@limiter.limit("10 per hour")
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
            "token": token,
            "user": {
                "id": new_user.id,
                "firstname": new_user.firstname,
                "lastname": new_user.lastname,
                "email": new_user.email,
            }
        }), 201
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500


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
# @limiter.limit("1 per hour")
@token_required
def delete_user(current_user, user_id):

    if current_user.id != user_id:
        return jsonify({'message': 'Unauthorized action'}), 403
    
    user = db.session.get(User, user_id)

    if user == None:
        return jsonify({'messge': 'invalid id'}), 400
    
    db.session.delete(user)
    db.session.commit()
    return jsonify({'message': f"deleted user {user_id}!"})

