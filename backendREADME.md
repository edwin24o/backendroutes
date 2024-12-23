Installations:

Setting Up SQLAlchemy
Before diving into relationships, let’s set up a basic SQLAlchemy model. First and foremost, to use SQLAlchemy we need to install it, and to do that we need to first set up our virtual environment.

- windows
python -m venv venv

- mac
python3 -m venv venv


Once we have created our virtual environment we need to activate the environment

- windows
venv\Scripts\activate

- mac
source venv/bin/activate

Now that we have our environment active we can start installing packages to the environment i.e. SQLAlchemy as well as our database interpreter that is going to be the translator between our python classes and SQL tables.

- windows 
pip install flask flask-sqlalchemy mysql-connector-python

-mac
pip3 install flask flask-sqlalchemy mysql-connector-python

======== installs ==================

- pip install flask-marshmallow marshmallow-sqlalchemy  
- pip install Flask-Limiter 
- pip install Flask-Caching
- pip install pyjwt
- pip install python-dotenv