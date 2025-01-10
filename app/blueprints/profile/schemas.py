from marshmallow import fields
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema
from app.models import Profile  # Import Profile model

class ProfileSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = Profile
        include_fk = True  # Include foreign key fields like user_id
        exclude = ["created_at"]  # Exclude fields you don't want to return (e.g., created_at)

    # Explicitly define profile fields (optional if already covered by SQLAlchemyAutoSchema)
    # id = fields.Int(dump_only=True)  # Only for reading the ID, not for input
    # user_id = fields.Int(required=True)  # Ensures that user_id is provided
    # full_name = fields.Str()  # Full name, derived from first and last name
    # email = fields.Str()  # Email for user identification
    # phone = fields.Str()  # Phone number
    # mobile = fields.Str()  # Mobile number
    # address = fields.Str()  # Address for the profile
    # avatar_url = fields.Str()  # Avatar URL for user profile picture
    # job_title = fields.Str()  # Job title
    # location = fields.Str()  # Location of the user
    # social_links = fields.Dict(keys=fields.Str(), values=fields.Str())  # Social media links in a dict

# Create an instance of the schema for profile creation or update
profile_schema = ProfileSchema()
