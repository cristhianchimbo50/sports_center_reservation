import pytest
from app import create_app, db
from app.models import Court
from datetime import date

@pytest.fixture
def client():
    # Crea una app de testing con base en memoria, agrega una cancha de prueba y limpia al final
    app = create_app({
        "TESTING": True,
        "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
        "WTF_CSRF_ENABLED": False,
        "SECRET_KEY": "testsecret"
    })
    with app.app_context():
        db.create_all()
        court = Court(name="Cancha Test", type="Fútbol", availability=True, price_per_hour=15.0)
        db.session.add(court)
        db.session.commit()
    with app.test_client() as client:
        yield client
    with app.app_context():
        db.drop_all()

def test_flujo_registro_reserva_pago(client):
    # 1. Registro de usuario
    resp = client.post('/register', data={
        'username': 'integuser',
        'password': '1234'
    }, follow_redirects=True)
    assert b'login' in resp.data.lower() or resp.status_code == 200

    # 2. Login
    resp = client.post('/login', data={
        'username': 'integuser',
        'password': '1234'
    }, follow_redirects=True)
    assert b'inicio' in resp.data.lower() or resp.status_code == 200

    # 3. Acceso al formulario de reserva
    resp = client.get('/add-reservation')
    assert b'reserva' in resp.data.lower()

    # 4. Obtener cancha de prueba
    with client.application.app_context():
        court = Court.query.filter_by(name="Cancha Test").first()
        assert court is not None
        court_id = court.id

    # 5. Crear reserva (ejemplo: reserva 07:00-08:00 hoy)
    form_data = {
        'court_id': court_id,
        'date': date.today().isoformat(),
        'slots': ['07:00-08:00']
    }
    resp = client.post('/add-reservation', data=form_data, follow_redirects=True)
    assert b'reserva' in resp.data.lower() or resp.status_code == 200

    # 6. Verificar reserva en la lista
    resp = client.get('/reservations')
    assert b'cancha test' in resp.data.lower()
    assert b'07:00' in resp.data or b'07:00 AM' in resp.data
