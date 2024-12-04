class Config:
    SECRET_KEY = 'admin'
    SQLALCHEMY_DATABASE_URI = 'postgresql://postgres:admin@localhost/automation'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
