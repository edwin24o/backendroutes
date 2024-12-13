from flask import request, jsonify
from app.blueprints.listings import listings_bp
from app.models import Listing, db
from marshmallow import ValidationError
from sqlalchemy import select
from app.blueprints.listings.schemas import listing_schema, listings_schema


@listings_bp.route("/", methods=["POST"])
def create_listing():
    try:
        listing_data = listing_schema.load(request.json)
        new_listing = Listing(
            user_id=listing_data["user_id"],
            skill_id=listing_data["skill_id"],
            title=listing_data["title"],
            description=listing_data.get("description")
        )
        db.session.add(new_listing)
        db.session.commit()
        return listing_schema.jsonify(new_listing), 201
    except ValidationError as e:
        return jsonify({"errors": e.messages}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@listings_bp.route("/", methods=["GET"])
def get_listings():
    query = select(Listing)
    listings = db.session.execute(query).scalars().all()
    return listings_schema.jsonify(listings), 200
