from flask import request, jsonify
from app.blueprints.listings import listings_bp
from app.models import Listing, db
from marshmallow import ValidationError
from sqlalchemy import select
from app.blueprints.listings.schemas import listing_schema, listings_schema, ListingSchema
from datetime import datetime
from app.utils.util import token_required
from flask import send_from_directory
from geopy.distance import geodesic
from geopy.geocoders import Nominatim
import os
import base64

# Image upload folder
UPLOAD_FOLDER = os.path.abspath('uploads/listing_images')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Route to create a new listing
@listings_bp.route("/create", methods=["POST"])
@token_required
def create_listing(current_user):
    try:
        listing_data = request.json
        print("Received Payload:", listing_data)

        # Validate the request payload
        validated_data = listing_schema.load(listing_data)

        if validated_data["type"] == "job" and not validated_data.get("wanted_skill"):
            return jsonify({"error": "Wanted Skill ID is required for job listings"}), 400

        if validated_data["type"] == "exchange" and (
            not validated_data.get("offered_skill") or not validated_data.get("wanted_skill")
        ):
            return jsonify({"error": "Offered and Wanted Skill IDs are required for exchanges"}), 400
        
         # Extract city, state, and zipCode from the payload
        city = validated_data.get("city")
        state = validated_data.get("state")
        zip_code = validated_data.get("zip_code")

        if not (city and state and zip_code):
            return jsonify({"error": "City, state, and zip code are required for location"}), 400
        
        image_data = validated_data.get("image")
        if image_data:
            try:
                # Decode the base64 image and save it as a file
                file_data = base64.b64decode(image_data.split(",")[1])  # Remove "data:image/*;base64,"
                filename = f"{current_user.id}_listing_{new_listing.id}.png"
                file_path = os.path.join(UPLOAD_FOLDER, filename)
                with open(file_path, "wb") as f:
                    f.write(file_data)
                image_path = f"/listing_images/{filename}"  # Relative path for retrieval
            except Exception as e:
                return jsonify({"error": f"Failed to process image: {str(e)}"}), 400
        else:
            image_path = None  # No image provided

        # Create a new Listing
        new_listing = Listing(
            user_id=current_user.id,
            title=validated_data["title"],
            description=validated_data.get("description"),
            city=validated_data["city"],
            state=validated_data["state"],
            zip_code=validated_data["zip_code"],
            type=validated_data["type"],
            offered_skill=validated_data.get("offered_skill"),
            wanted_skill=validated_data.get("wanted_skill"),
            image=image_path,
            created_at=datetime.utcnow(),
        )
        db.session.add(new_listing)
        db.session.commit()

        if image_data:
            filename = f"{current_user.id}_listing_{new_listing.id}.png"
            file_path = os.path.join(UPLOAD_FOLDER, filename)
            with open(file_path, "wb") as f:
                f.write(file_data)
                new_listing.image = f"/listing_images/{filename}"
                db.session.commit()

        return jsonify({
            "message": "Listing created successfully",
            "listing": listing_schema.dump(new_listing)
        }), 201
    except ValidationError as ve:
        return jsonify({"error": ve.messages}), 400
    except Exception as e:
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500

# Route to serve image files
@listings_bp.route("/listing_images/<filename>", methods=["GET"])
def serve_image(filename):
    return send_from_directory(UPLOAD_FOLDER, filename)

# Route to get all listings
@listings_bp.route("/search", methods=["GET"])
def search_listings():
    try:
        # Extract filters
        type_filter = request.args.get("type")  # 'job' or 'exchange'
        city = request.args.get("city")  # City for location
        state = request.args.get("state")  # State for location
        zip_code = request.args.get("zip_code")  # ZIP code for proximity
        wanted_skill = request.args.get("wanted_skill")  # Skill wanted
        offered_skill = request.args.get("offered_skill")  # Skill offered
        proximity = request.args.get("proximity", type=int)  # Distance in miles

        # Start building the query
        query = Listing.query

        if type_filter:
            query = query.filter(Listing.type == type_filter)
        if city:
            query = query.filter(Listing.city.ilike(f"%{city}%"))  # Case-insensitive match
        if state:
            query = query.filter(Listing.state.ilike(f"%{state}%"))
        if wanted_skill:
            query = query.filter(Listing.wanted_skill.ilike(f"%{wanted_skill}%"))
        if offered_skill:
            query = query.filter(Listing.offered_skill.ilike(f"%{offered_skill}%"))

        # Fetch all listings that match the filters so far
        listings = query.all()

        # Apply proximity filter if zip_code and proximity are provided
        if zip_code and proximity:
            geolocator = Nominatim(user_agent="listings_search")
            location = geolocator.geocode({"postalcode": zip_code, "country": "United States"})

            if not location:
                return jsonify({"error": "Invalid ZIP code for proximity filtering"}), 400

            user_location = (location.latitude, location.longitude)
            listings_within_proximity = []

            for listing in listings:
                if listing.zip_code:
                    listing_location = geolocator.geocode(
                        {"postalcode": listing.zip_code, "country": "United States"}
                    )
                    if listing_location:
                        listing_coords = (listing_location.latitude, listing_location.longitude)
                        distance = geodesic(user_location, listing_coords).miles
                        if distance <= proximity:
                            listings_within_proximity.append(listing)

            listings = listings_within_proximity

        # Serialize and return the filtered listings
        return listings_schema.jsonify(listings), 200

    except Exception as e:
        print(f"Error during search: {e}")
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

