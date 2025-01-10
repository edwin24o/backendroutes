from flask import request, jsonify
from app.blueprints.listings import listings_bp
from app.models import Listing, db
from marshmallow import ValidationError
from sqlalchemy import select
from app.blueprints.listings.schemas import listing_schema, listings_schema, ListingSchema
from datetime import datetime
from app.utils.util import token_required


# Route to create a new listing
@listings_bp.route("/create", methods=["POST"])
@token_required
def create_listing(current_user):
    try:
        listing_data = request.json

        # Validate the request payload
        validated_data = listing_schema.load(listing_data)

        # Create a new Listing
        new_listing = Listing(
            user_id=current_user.id,
            skill_id=validated_data.get("skill_id"),
            title=validated_data["title"],
            description=validated_data.get("description"),
            location=validated_data.get("location"),
            type=validated_data["type"],
            offered_skill=validated_data.get("offered_skill"),
            wanted_skill=validated_data.get("wanted_skill"),
            created_at=datetime.utcnow(),
        )
        db.session.add(new_listing)
        db.session.commit()

        return jsonify({
            "message": "Listing created successfully",
            "listing": listing_schema.dump(new_listing)
        }), 201
    except ValidationError as ve:
        return jsonify({"error": ve.messages}), 400
    except Exception as e:
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500


# Route to get all listings
@listings_bp.route("/search", methods=["GET"])
def search_listings():
    try:
        # Fetch query parameters from the request
        skill_id = request.args.get("skill_id", type=int)
        user_id = request.args.get("user_id", type=int)
        location = request.args.get("location", type=str)
        type_filter = request.args.get("type", type=str)  # 'job' or 'exchange'
        wanted_skill = request.args.get("wanted_skill", type=int)
        offered_skill = request.args.get("offered_skill", type=int)

        # Build the query dynamically
        query = Listing.query

        if skill_id:
            query = query.filter(Listing.skill_id == skill_id)
        if user_id:
            query = query.filter(Listing.user_id == user_id)
        if location:
            query = query.filter(Listing.location.ilike(f"%{location}%"))  # Case-insensitive partial match
        if type_filter:
            query = query.filter(Listing.type == type_filter)
        if wanted_skill:
            query = query.filter(Listing.wanted_skill == wanted_skill)
        if offered_skill:
            query = query.filter(Listing.offered_skill == offered_skill)

        # Execute the query and fetch results
        listings = query.all()

        return listings_schema.jsonify(listings), 200
    except Exception as e:
        return jsonify({"error": "An error occurred while searching listings"}), 500

@listings_bp.route("/", methods=["GET"])
def get_all_listings():
    try:
        # Query all listings
        query = db.session.execute(select(Listing).order_by(Listing.created_at.desc()))
        listings = query.scalars().all()

        return jsonify(listings_schema.dump(listings)), 200
    except Exception as e:
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500