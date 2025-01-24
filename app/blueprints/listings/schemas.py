from app.extensions import ma
from app.models import Listing
from marshmallow import fields,Schema, validate, post_load, ValidationError

class ListingSchema(Schema):
    id = fields.Int(dump_only=True)
    user_id = fields.Int(dump_only=True)
    title = fields.Str(required=True)
    description = fields.Str(allow_none=True)
    city = fields.Str(required=True)  
    state = fields.Str(required=True)  
    zip_code = fields.Str(required=True)  
    type = fields.Str(
        required=True,
        validate=validate.OneOf(["job", "skill_exchange"]),
    )
    offered_skill = fields.Int(required=False, allow_none=True)  # For skill exchanges
    wanted_skill = fields.Int(required=False, allow_none=True)  # For skill exchanges
    image = fields.Str(required=False, allow_none=True) 
    created_at = fields.DateTime(dump_only=True)  

    @post_load
    def validate_exchange(self, data, **kwargs):
        """Ensure required fields for skill_exchange are present."""
        if data.get("type") == "skill_exchange":
            if not data.get("offered_skill") or not data.get("wanted_skill"):
                raise ValidationError(
                    "For skill_exchange, both 'offered_skill' and 'wanted_skill' are required."
                )
        return data
    
listing_schema = ListingSchema()
listings_schema = ListingSchema(many=True)

