from . import db
from flask_login import UserMixin

class User(UserMixin, db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(128), nullable=False)
    role = db.Column(db.String(20), default='cliente', nullable=False)  # 'cliente' o 'administrador'
    reservations = db.relationship('Reservation', back_populates='user', cascade='all, delete-orphan')

    def is_admin(self):
        return self.role == 'administrador'

    def is_cliente(self):
        return self.role == 'cliente'


class Court(db.Model):
    __tablename__ = 'courts'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True, nullable=False)
    type = db.Column(db.String(50), nullable=False)  # Fútbol, Tenis, Básquet
    availability = db.Column(db.Boolean, default=True)
    price_per_hour = db.Column(db.Numeric(10, 2), default=0)
    reservations = db.relationship('Reservation', back_populates='court', cascade='all, delete-orphan')
    schedules = db.relationship('CourtSchedule', back_populates='court', cascade='all, delete-orphan')


class Reservation(db.Model):
    __tablename__ = 'reservations'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    court_id = db.Column(db.Integer, db.ForeignKey('courts.id'), nullable=False)
    date = db.Column(db.Date, nullable=False)
    status = db.Column(db.String(20), default='Pending')
    user = db.relationship('User', back_populates='reservations')
    court = db.relationship('Court', back_populates='reservations')
    payment = db.relationship('Payment', back_populates='reservation', uselist=False)
    slots = db.relationship('ReservationSlot', back_populates='reservation', cascade='all, delete-orphan')


class ReservationSlot(db.Model):
    __tablename__ = 'reservation_slots'

    id = db.Column(db.Integer, primary_key=True)
    reservation_id = db.Column(db.Integer, db.ForeignKey('reservations.id'), nullable=False)
    start_time = db.Column(db.Time, nullable=False)
    end_time = db.Column(db.Time, nullable=False)
    reservation = db.relationship('Reservation', back_populates='slots')


class Payment(db.Model):
    __tablename__ = 'payments'

    id = db.Column(db.Integer, primary_key=True)
    reservation_id = db.Column(db.Integer, db.ForeignKey('reservations.id'), nullable=False)
    amount = db.Column(db.Numeric(10, 2), nullable=False)
    payment_date = db.Column(db.DateTime, nullable=False)
    status = db.Column(db.String(20), default='Paid')
    reservation = db.relationship('Reservation', back_populates='payment')


class CourtSchedule(db.Model):
    __tablename__ = 'court_schedules'

    id = db.Column(db.Integer, primary_key=True)
    court_id = db.Column(db.Integer, db.ForeignKey('courts.id'), nullable=False)
    day_of_week = db.Column(db.String(20), nullable=False)  # Ej: 'Lunes', 'Martes'
    start_time = db.Column(db.Time, nullable=False)
    end_time = db.Column(db.Time, nullable=False)
    court = db.relationship('Court', back_populates='schedules')
