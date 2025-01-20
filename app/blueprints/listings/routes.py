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

        if validated_data["type"] == "job" and not validated_data.get("wanted_skill"):
            return jsonify({"error": "Wanted Skill ID is required for job listings"}), 400

        if validated_data["type"] == "exchange" and (
            not validated_data.get("offered_skill") or not validated_data.get("wanted_skill")
        ):
            return jsonify({"error": "Offered and Wanted Skill IDs are required for exchanges"}), 400

        # Create a new Listing
        new_listing = Listing(
            user_id=current_user.id,
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
        type_filter = request.args.get("type")  # 'job' or 'exchange'
        location = request.args.get("location", type=str)
        wanted_skill = request.args.get("wanted_skill", type=str)

        # Build the query dynamically
        query = Listing.query

        if type_filter:
            query = query.filter(Listing.type == type_filter)  # Filter by type
        if location:
            query = query.filter(Listing.location.ilike(f"%{location}%"))  # Case-insensitive location filter
        if type_filter == "exchange" and wanted_skill:
            query = query.filter(Listing.wanted_skill.ilike(f"%{wanted_skill}%"))

        # Execute the query and fetch results
        listings = query.all()

        return listings_schema.jsonify(listings), 200
    except Exception as e:
        return jsonify({"error": "An error occurred while searching listings"}), 500

@listings_bp.route("/", methods=["GET"])
def get_all_listings():
    try:
        page = request.args.get("page", default=1, type=int)
        per_page = request.args.get("per_page", default=10, type=int)

        # Query all listings
        query = db.session.execute(select(Listing).order_by(Listing.created_at.desc()))
        listings = query.scalars().all()

        return jsonify(listings_schema.dump(listings)), 200
    except Exception as e:
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500
    
@listings_bp.route("/<int:listing_id>", methods=["GET"])
def get_listing(listing_id):
    try:
        print(f"Fetching listing with ID: {listing_id}")
        listing = db.session.get(Listing, listing_id)
        if not listing:
            print(f"Listing not found for ID: {listing_id}")
            return jsonify({"error": "Listing not found"}), 404

        # Serialize the listing data using Marshmallow
        serialized_data = listing_schema.dump(listing)
        print("Listing fetched successfully:", serialized_data)
        return jsonify(serialized_data), 200
    except Exception as e:
        print(f"An error occurred: {e}")
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500

