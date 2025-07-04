from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_user, logout_user, login_required
from werkzeug.security import generate_password_hash, check_password_hash
from .models import Reservation
from . import db, login_manager
from .models import User, Court

from .models import Reservation
from datetime import date

# Definir el Blueprint
main_bp = Blueprint('main', __name__, url_prefix='/')


# Auth

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


@main_bp.route('/')
def home():
    return render_template('home.html')


@main_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        if User.query.filter_by(username=username).first():
            flash('El usuario ya existe')
            return redirect(url_for('main.register'))

        hashed_password = generate_password_hash(password)
        user = User(username=username, password=hashed_password)
        db.session.add(user)
        db.session.commit()

        flash('¡Registro exitoso!')
        return redirect(url_for('main.login'))

    return render_template('register.html')


@main_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password, password):
            login_user(user)
            return redirect(url_for('main.home'))
        else:
            flash('Usuario o contraseña incorrectos')

    return render_template('login.html')


@main_bp.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('main.login'))


# Cancha

@main_bp.route('/courts')
@login_required
def list_courts():
    courts = Court.query.all()
    return render_template('courts.html', courts=courts)


@main_bp.route('/add-court', methods=['GET', 'POST'])
@login_required
def add_court():
    if request.method == 'POST':
        name = request.form['name']
        type_ = request.form['type']

        if Court.query.filter_by(name=name).first():
            flash('Ya existe una cancha con ese nombre')
            return redirect(url_for('main.add_court'))

        court = Court(name=name, type=type_, availability=True)
        db.session.add(court)
        db.session.commit()

        flash('Cancha agregada exitosamente')
        return redirect(url_for('main.list_courts'))

    return render_template('add_court.html')

# Reserva

@main_bp.route('/reservations')
@login_required
def list_reservations():
    reservations = Reservation.query.all()
    return render_template('reservations.html', reservations=reservations)


@main_bp.route('/add-reservation', methods=['GET', 'POST'])
@login_required
def add_reservation():
    courts = Court.query.all()

    if request.method == 'POST':
        court_id = request.form['court_id']
        date_ = request.form['date']
        time_slot = request.form['time_slot']

        reservation = Reservation(
            user_id=current_user.id,
            court_id=court_id,
            date=date.fromisoformat(date_),
            time_slot=time_slot,
            status='Pending'
        )
        db.session.add(reservation)
        db.session.commit()

        flash('Reserva creada exitosamente')
        return redirect(url_for('main.list_reservations'))

    return render_template('add_reservation.html', courts=courts)