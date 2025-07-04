from . import db
from flask_login import UserMixin

# User
class User(UserMixin, db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(128), nullable=False)

    # Relación con reservas
    reservations = db.relationship('Reservation', back_populates='user')

# Court
class Court(db.Model):
    __tablename__ = 'courts'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True, nullable=False)
    type = db.Column(db.String(50), nullable=False)  # Fútbol, Tenis, Básquet
    availability = db.Column(db.Boolean, default=True)

    # Relación con reservas
    reservations = db.relationship('Reservation', back_populates='court')

# Reservation
class Reservation(db.Model):
    __tablename__ = 'reservations'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    court_id = db.Column(db.Integer, db.ForeignKey('courts.id'), nullable=False)
    date = db.Column(db.Date, nullable=False)
    time_slot = db.Column(db.String(20), nullable=False)  # Ejemplo: "10:00 - 11:00"
    status = db.Column(db.String(20), default='Pending')

    # Relaciones
    user = db.relationship('User', back_populates='reservations')
    court = db.relationship('Court', back_populates='reservations')
    payment = db.relationship('Payment', back_populates='reservation', uselist=False)

# Payment
class Payment(db.Model):
    __tablename__ = 'payments'

    id = db.Column(db.Integer, primary_key=True)
    reservation_id = db.Column(db.Integer, db.ForeignKey('reservations.id'), nullable=False)
    amount = db.Column(db.Numeric(10, 2), nullable=False)
    payment_date = db.Column(db.DateTime, nullable=False)
    status = db.Column(db.String(20), default='Paid')

    # Relación con reserva
    reservation = db.relationship('Reservation', back_populates='payment')
