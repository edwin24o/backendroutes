from app.extensions import ma
from app.models import Transaction

class TransactionSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Transaction

transaction_schema = TransactionSchema()
transactions_schema = TransactionSchema(many=True)
