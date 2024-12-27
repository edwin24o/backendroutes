from flask import request, jsonify
from app.models import User, Listing, db
from app.blueprints.search import search_bp
from .schemas import UserSchema, JobSchema

# Initialize the schemas
user_schema = UserSchema()
job_schema = JobSchema(many=True)

# User Search Route
@search_bp.route("/search/users", methods=["GET"])
def search_users():
    query = request.args.get('query', '')  # Search term (e.g., name, email)
    location = request.args.get('location', '')  # Optional filter by location

    # Filter users based on the query and location
    user_query = User.query.filter(
        (User.firstname.ilike(f'%{query}%')) |
        (User.lastname.ilike(f'%{query}%')) |
        (User.email.ilike(f'%{query}%')) |
        (User.location.ilike(f'%{query}%'))
    )

    if location:
        user_query = user_query.filter(User.location.ilike(f'%{location}%'))

    users = user_query.all()

    return jsonify([user_schema.dump(user) for user in users])

# Job Search Route
@search_bp.route("/search/jobs", methods=["GET"])
def search_jobs():
    query = request.args.get('query', '')  # Search term (e.g., job title)
    job_type = request.args.get('job_type', '')  # Job type filter (full-time, part-time)
    location = request.args.get('location', '')  # Location filter

    # Basic query for job title matching
    job_query = Listing.query.filter(Listing.title.ilike(f'%{query}%'))

    # Add filters for job type and location
    if job_type:
        job_query = job_query.filter(Listing.job_type.ilike(f'%{job_type}%'))
    if location:
        job_query = job_query.filter(Listing.location.ilike(f'%{location}%'))

    jobs = job_query.all()

    # Use job schema to serialize the job data
    return jsonify([job_schema.dump(job) for job in jobs])
