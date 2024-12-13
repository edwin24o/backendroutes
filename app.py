from app import create_app
from app.models import db

app = create_app('DevelopmentConfig')




if __name__ == '__main__':
    with app.app_context():
     # db.drop_all()
     db.create_all()

#         with app.app_context():
#             pass

     app.run(debug=True)