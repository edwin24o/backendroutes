from flask import request, jsonify
from app.blueprints.messages import messages_bp
from app.models import Message, db, Listing
from app.utils.util import token_required
from marshmallow import ValidationError
from datetime import datetime
from app.utils.util import token_required
from app.blueprints.messages.schemas import message_schema, messages_schema

@messages_bp.route("/create", methods=["POST"])
@token_required
def create_message(current_user):
    try:
        message_data = request.json

        # Validate the data
        recipient_id = message_data.get("recipient_id")
        content = message_data.get("content")
        listing_id = message_data.get("listing_id")
        label = message_data.get("label")
        reply_to_id = message_data.get("reply_to_id")

        if not recipient_id or not content:
            return jsonify({"error": "Recepient ID and content are required"}), 400

        # Create a new message
        new_message = Message(
            sender_id=current_user.id,
            recipient_id=recipient_id,
            content=content,
            listing_id=listing_id,
            label=label,
            reply_to_id=reply_to_id
        )
        db.session.add(new_message)
        db.session.commit()

        return jsonify({"message": "Message sent successfully"}), 201
    except Exception as e:
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500


@messages_bp.route("/send", methods=["POST"])
@token_required
def send_message(current_user):
    try:
        data = request.json

        recipient_id = data.get("recipient_id")
        content = data.get("content")
        listing_id = data.get("listing_id")  # Optional: If linked to a listing
        reply_to_id = data.get("reply_to_id")  # Reference the original message if it's a reply

        # Validate required fields
        if not recipient_id or not content:
            return jsonify({"error": "Recipient ID and content are required"}), 400

        # Create a new message
        new_message = Message(
            sender_id=current_user.id,
            recipient_id=recipient_id,
            content=content,
            listing_id=listing_id,  
            reply_to_id=reply_to_id,  
            created_at=datetime.utcnow(),
        )

        db.session.add(new_message)
        db.session.commit()

        return jsonify({"message": "Message sent successfully"}), 201
    except Exception as e:
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500



@messages_bp.route("/", methods=["GET"])
@token_required
def get_messages(current_user):
    try:
        # Fetch messages where the logged-in user is the recipient
        messages = (
            db.session.query(Message, Listing)
            .outerjoin(Listing, Message.listing_id == Listing.id)
            .filter(Message.recipient_id == current_user.id)
            .order_by(Message.created_at.desc())
            .all()
        )

        messages_list = [
            {
                "id": msg.id,
                "recipient_id": msg.recipient_id,
                "content": msg.content,
                "listing_id": msg.listing_id,
                "listing_title": msg.listing.title if msg.listing else None,
                "listing_description": msg.listing.description if msg.listing else None,
                "created_at": msg.created_at,
            }
            for msg, listing in messages
        ]
        return jsonify(messages_list), 200
    except Exception as e:
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500


@messages_bp.route("/sent", methods=["GET"])
@token_required
def get_sent_messages(current_user):
    try:
        
        messages = (
            db.session.query(Message, Listing)
            .outerjoin(Listing, Message.listing_id == Listing.id)
            .filter(Message.sender_id == current_user.id)
            .order_by(Message.created_at.desc())
            .all()
        )

        sent_messages_list = [
            {
                "id": msg.id,
                "recipient_id": msg.recipient_id,
                "content": msg.content,
                "listing_id": msg.listing_id,
                "listing_title": msg.listing.title if msg.listing else None,
                "listing_description": msg.listing.description if msg.listing else None,
                "created_at": msg.created_at,
            }
            for msg, listing in messages
        ]
        return jsonify(sent_messages_list), 200
    except Exception as e:
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500

@messages_bp.route("/reply", methods=["POST"])
@token_required
def reply_message(current_user):
    try:
        data = request.json

        print("Incoming data:", data)
        
        recipient_id = data.get("recipient_id")
        content = data.get("content")
        listing_id = data.get("listing_id")
        reply_to_id = data.get("reply_to_id")  # Reply to a specific message

      
        if not recipient_id or not content or not listing_id:
            return jsonify({"error": "Recipient ID, content, and listing ID are required"}), 400
        
        original_message = db.session.get(Message, reply_to_id)
        if not original_message:
            return jsonify({"error": "Original message not found"}), 404

     
        recipient_id = original_message.sender_id

        # Log values for debugging
        print(f"Recipient ID: {recipient_id}, Content: {content}, Listing ID: {listing_id}, Reply To: {reply_to_id}")

        # Create a new message
        new_message = Message(
            sender_id=current_user.id,
            recipient_id=recipient_id,
            content=content,
            listing_id=listing_id,
            reply_to_id=reply_to_id,  
            created_at=datetime.utcnow()
        )

        db.session.add(new_message)
        db.session.commit()

        return jsonify(message_schema.dump(new_message)), 201
    except Exception as e:
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500

