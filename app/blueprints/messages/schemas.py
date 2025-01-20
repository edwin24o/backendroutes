from marshmallow import Schema, fields

class MessageSchema(Schema):
    id = fields.Int(dump_only=True)
    sender_id = fields.Int(required=True)
    recipient_id = fields.Int(required=True)
    content = fields.Str(required=True)
    created_at = fields.DateTime(dump_only=True)
    listing_id = fields.Int(required=False, allow_none=True)
    label = fields.Str(required=False, allow_none=True)
    reply_to_id = fields.Int(required=False, allow_none=True)

# Create schema instances for single and multiple messages
message_schema = MessageSchema()
messages_schema = MessageSchema(many=True)
