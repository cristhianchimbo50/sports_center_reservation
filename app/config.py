class Config:
    SECRET_KEY = 'clave-super-secretisima'
    SQLALCHEMY_DATABASE_URI = (
        'postgresql://postgres:randomcch1203@localhost:5432/db_sportcenter'
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
