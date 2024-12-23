from flask import request, jsonify
from app.blueprints.users import users_bp
from marshmallow import ValidationError
from app.models import User, db
from sqlalchemy import select
from app.blueprints.users.schemas import user_schema, users_schema, login_schema
from werkzeug.security import check_password_hash, generate_password_hash
from app.models import User
from app.extensions import limiter
from app.utils.util import encode_token, token_required
from flask_cors import cross_origin

# Login schema 

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

        response = {
            "message": 'successfully logged in',
            "status": "success",
            "token": token
        }

        return jsonify(response), 200

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

        return user_schema.jsonify(new_user), 201

    except ValidationError as e:
#         # Return validation error messages
        return jsonify({"errors": e.messages}), 400
    except Exception as e:
#         # Catch other exceptions
        return jsonify({"error": str(e)}), 500
    
# @users_bp.route("/signup", methods=['POST'])
# @cross_origin()
# def sign_up_user():
#     try:
#         # Validate and deserialize input data for sign-up
#         user_data = user_schema.load(request.json)

#         # Check if the user already exists based on email
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
#             password=password_hash,
#             rating=user_data.get('rating', 0)
#         )

#         # Add user to the database
#         db.session.add(new_user)
#         db.session.commit()

#         # Generate a token for the newly created user
#         token = encode_token(new_user.id)  # Generate JWT token

#         # Return the newly created user and token
#         response = {
#             "message": 'User created successfully',
#             "status": "success",
#             "token": token  # Send token so the user can be logged in immediately
#         }

#         return jsonify(response), 201

#     except ValidationError as e:
#         return jsonify({"errors": e.messages}), 400
#     except Exception as e:
#         return jsonify({"error": str(e)}), 500



# @users_bp.route("/", methods=['OPTIONS'])
# @cross_origin()
# def handle_options():
#     return jsonify({"message": "OK"})


@users_bp.route("/users", methods=['OPTIONS'])
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



   #     # Get login data from request
    #     login_data = request.json
    #     email = login_data.get('email')
    #     password = login_data.get('password')  # Password should be sent in plaintext

    #     # Check if email and password are provided
    #     if not email or not password:
    #         return jsonify({"error": "Email and password are required."}), 400

    #     # Query the database for the user with the given email
    #     user = User.query.filter_by(email=email).first()

    #     # Check if user exists
    #     if not user:
    #         return jsonify({"error": "User not found."}), 404

    #     # Check if the provided password matches the hashed password
    #     if not check_password_hash(user.password, password):  # Compare hashed password with the provided password
    #         return jsonify({"error": "Invalid password."}), 401

    #     # Return a success message (you can also generate and return a JWT token here)
    #     return jsonify({"message": "Login successful", "user": user_schema.dump(user)}), 200

    # except Exception as e:
    #     # Catch other exceptions and return an error
    #     return jsonify({"error": str(e)}), 500