from marshmallow import Schema, fields
from app.models import Profile  # Import Profile model
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema

class ProfileSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = Profile
        include_fk = True  # Include foreign key fields like user_id
        exclude = ["created_at"]  # Exclude fields you don't want to return (e.g., created_at)

    # Explicitly define profile fields
    id = fields.Int(dump_only=True)
    user_id = fields.Int(required=True)  # Ensure that user_id is provided in the profile data
    bio = fields.Str()
    avatar_url = fields.Str()
    location = fields.Str()
    contact_number = fields.Str()

# Create an instance of the schema for profile creation or update
profile_schema = ProfileSchema()
