from app import create_app, db
from sqlalchemy import text

app = create_app()

with app.app_context():
    try:
        result = db.session.execute(text("SELECT datname FROM pg_database;"))
        print("Conexión exitosa. Bases de datos disponibles:")
        for row in result:
            print(row[0])
    except Exception as e:
        print("Error al conectar con la base de datos:")
        print(e)
