import pytest
from app.models import User, Court, Reservation, ReservationSlot, Payment, CourtSchedule
from werkzeug.security import generate_password_hash
from datetime import date, time, datetime

@pytest.fixture
def user():
    return User(username='cliente1', password=generate_password_hash('1234'), role='cliente')

@pytest.fixture
def admin():
    return User(username='admin1', password=generate_password_hash('admin'), role='administrador')

@pytest.fixture
def court():
    return Court(name='Cancha Fútbol', type='Fútbol', availability=True, price_per_hour=10.0)

@pytest.fixture
def schedule(court):
    return CourtSchedule(court_id=1, day_of_week='Lunes', start_time=time(7, 0), end_time=time(8, 0))

@pytest.fixture
def reservation(user, court):
    return Reservation(user_id=1, court_id=1, date=date.today(), status='Paid')

@pytest.fixture
def slot():
    return ReservationSlot(reservation_id=1, start_time=time(7, 0), end_time=time(8, 0))

@pytest.fixture
def payment(reservation):
    return Payment(reservation_id=1, amount=10.0, payment_date=datetime.now(), status='Paid')

def test_user_creation(user):
    assert user.username == 'cliente1'
    assert user.role == 'cliente'
    assert user.password != '1234'

def test_admin_role(admin):
    assert admin.role == 'administrador'

def test_court_creation(court):
    assert court.name == 'Cancha Fútbol'
    assert court.type == 'Fútbol'
    assert court.availability is True
    assert court.price_per_hour == 10.0

def test_court_schedule(schedule):
    assert schedule.day_of_week == 'Lunes'
    assert schedule.start_time == time(7, 0)
    assert schedule.end_time == time(8, 0)

def test_reservation_creation(reservation):
    assert reservation.status == 'Paid'
    assert isinstance(reservation.date, date)

def test_slot_times(slot):
    assert slot.start_time < slot.end_time
    assert slot.start_time == time(7, 0)
    assert slot.end_time == time(8, 0)

def test_payment(payment):
    assert payment.amount == 10.0
    assert payment.status == 'Paid'
    assert isinstance(payment.payment_date, datetime)

def test_user_roles(user, admin):
    assert hasattr(user, 'is_cliente')
    assert user.is_cliente()
    assert not user.is_admin()
    assert admin.is_admin()
