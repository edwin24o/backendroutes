import os

class DevelopmentConfig:
    SQLALCHEMY_DATABASE_URI = os.environ.get('SQLALCHEMY_DATABASE_URI')
    DEBUG = True
    CACHE_TYPE = "SimpleCache"


class TextingConfig:
    pass

class ProductionConfig:
    pass