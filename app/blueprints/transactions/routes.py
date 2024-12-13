from app.blueprints.transactions import transactions_bp
from flask import request, jsonify
from marshmallow import ValidationError
from app.models import Transaction, db
from app.blueprints.transactions.schemas import transactions_schema, transaction_schema


@transactions_bp.route("/", methods=["POST"])
def create_transaction():
    try:
        # Validate and deserialize input data
        transaction_data = transaction_schema.load(request.json)

        # Create a new Transaction instance
        new_transaction = Transaction(
            amount=transaction_data["amount"],
            user_id=transaction_data["user_id"],
            listing_id=transaction_data.get("listing_id"),  # Optional if allowed
            transaction_date=transaction_data.get("transaction_date"),  # Optional field
            status=transaction_data.get("status", "Pending")  # Default status
        )

        # Add the new transaction to the database
        db.session.add(new_transaction)
        db.session.commit()

        # Return the newly created transaction
        return jsonify(transaction_schema.dump(new_transaction)), 201

    except ValidationError as e:
        # Return validation error messages
        return jsonify({"errors": e.messages}), 400
    except Exception as e:
        # Catch other exceptions
        return jsonify({"error": str(e)}), 500
    

@transactions_bp.route("/", methods=["GET"])
def get_transactions():
    transaction_id = request.args.get("id")

    if transaction_id:
        # Fetch a specific transaction by ID
        transaction = Transaction.query.get(transaction_id)
        if transaction:
            return jsonify(transaction_schema.dump(transaction)), 200
        return jsonify({"error": "Transaction not found"}), 404

    # Fetch all transactions
    transactions = Transaction.query.all()
    return jsonify(transactions_schema.dump(transactions)), 200


# [DELETE] - Delete a Transaction by ID
@transactions_bp.route("/<int:id>", methods=["DELETE"])
def delete_transaction(id):
    try:
        # Find the transaction by ID
        transaction = Transaction.query.get(id)
        if not transaction:
            return jsonify({"error": "Transaction not found"}), 404

        # Delete the transaction
        db.session.delete(transaction)
        db.session.commit()
        return jsonify({"message": "Transaction deleted successfully"}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
