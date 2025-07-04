from . import db, login_manager
from flask import Blueprint, render_template, redirect, url_for, request, flash, jsonify
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from .models import User, Court, Reservation, CourtSchedule, ReservationSlot, Payment
import datetime
from functools import wraps

# Definir el Blueprint
main_bp = Blueprint('main', __name__, url_prefix='/')


# ------------------ Decoradores de Rol ------------------

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin():
            flash('Acceso restringido a administradores.')
            return redirect(url_for('main.home'))
        return f(*args, **kwargs)
    return decorated_function

def cliente_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_cliente():
            flash('Solo clientes pueden acceder a esta sección.')
            return redirect(url_for('main.home'))
        return f(*args, **kwargs)
    return decorated_function

# ------------------ Auth ------------------

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
        user = User(username=username, password=hashed_password, role='cliente')  # Siempre cliente
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

# ------------------ Gestión de Canchas ------------------

@main_bp.route('/courts')
@login_required
def list_courts():
    if current_user.is_admin():
        courts = Court.query.all()
        return render_template('courts.html', courts=courts, admin=True)
    else:
        courts = Court.query.filter_by(availability=True).all()
        return render_template('courts.html', courts=courts, admin=False)

@main_bp.route('/add-court', methods=['GET', 'POST'])
@admin_required
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

# ------------------ Gestión de Horarios de Canchas ------------------

@main_bp.route('/court-schedules/<int:court_id>', methods=['GET', 'POST'])
@admin_required
def manage_court_schedule(court_id):
    court = Court.query.get_or_404(court_id)

    if request.method == 'POST':
        day_of_week = request.form['day_of_week']
        start_time = request.form['start_time']
        end_time = request.form['end_time']

        schedule = CourtSchedule(
            court_id=court.id,
            day_of_week=day_of_week,
            start_time=start_time,
            end_time=end_time
        )
        db.session.add(schedule)
        db.session.commit()

        flash('Horario agregado correctamente')
        return redirect(url_for('main.manage_court_schedule', court_id=court.id))

    schedules = CourtSchedule.query.filter_by(court_id=court.id).all()
    return render_template('manage_court_schedule.html', court=court, schedules=schedules)

# ------------------ Reservas ------------------

@main_bp.route('/reservations')
@login_required
def list_reservations():
    if current_user.is_admin():
        reservations = Reservation.query.order_by(Reservation.date.desc()).all()
        return render_template('reservations.html', reservations=reservations, admin=True)
    else:
        reservations = Reservation.query.filter_by(user_id=current_user.id).order_by(Reservation.date.desc()).all()
        return render_template('reservations.html', reservations=reservations, admin=False)

@main_bp.route('/add-reservation', methods=['GET', 'POST'])
@cliente_required
def add_reservation():
    courts = Court.query.filter_by(availability=True).all()

    if request.method == 'POST':
        court_id_str = request.form.get('court_id')
        date_str = request.form.get('date')
        selected_slots = request.form.getlist('slots')  # slots es una lista de strings 'HH:MM-HH:MM'

        if not court_id_str or not date_str or not selected_slots:
            flash('Debe seleccionar cancha, fecha y al menos un horario disponible.')
            return redirect(url_for('main.add_reservation'))

        court_id = int(court_id_str)
        selected_date = datetime.date.fromisoformat(date_str)

        # Validación: asegurarse que todos los horarios elegidos estén disponibles
        for slot in selected_slots:
            start_str, end_str = slot.split('-')
            start_time = datetime.datetime.strptime(start_str, '%H:%M').time()
            end_time = datetime.datetime.strptime(end_str, '%H:%M').time()
            conflicto = (
                db.session.query(ReservationSlot)
                .join(Reservation)
                .filter(
                    Reservation.court_id == court_id,
                    Reservation.date == selected_date,
                    ReservationSlot.start_time == start_time,
                    ReservationSlot.end_time == end_time
                ).first()
            )
            if conflicto:
                flash(f'La franja {slot} ya está reservada. Seleccione solo horarios disponibles.')
                return redirect(url_for('main.add_reservation'))

        # Crear la reserva principal
        reservation = Reservation(
            user_id=current_user.id,
            court_id=court_id,
            date=selected_date,
            status='Paid'  # simulamos el pago exitoso
        )
        db.session.add(reservation)
        db.session.commit()  # Necesario para obtener el reservation.id

        # Insertar todos los slots seleccionados
        for slot in selected_slots:
            start_str, end_str = slot.split('-')
            start_time = datetime.datetime.strptime(start_str, '%H:%M').time()
            end_time = datetime.datetime.strptime(end_str, '%H:%M').time()
            slot_obj = ReservationSlot(
                reservation_id=reservation.id,
                start_time=start_time,
                end_time=end_time
            )
            db.session.add(slot_obj)
        db.session.commit()

        flash('Reserva creada exitosamente.')
        return redirect(url_for('main.list_reservations'))

    return render_template('add_reservation.html', courts=courts)

# ------------------ API Horarios disponibles ------------------

@main_bp.route('/api/available-hours', methods=['GET'])
@login_required
def api_available_hours():
    court_id = request.args.get('court_id')
    date_str = request.args.get('date')

    if not court_id or not date_str:
        return jsonify({'error': 'Parámetros incompletos'}), 400

    try:
        court_id = int(court_id)
        selected_date = datetime.date.fromisoformat(date_str)
    except Exception:
        return jsonify({'error': 'Datos inválidos'}), 400

    slots = []
    for h in range(5, 24):
        start_time = datetime.time(hour=h, minute=0)
        end_time = (datetime.datetime.combine(datetime.date.today(), start_time) + datetime.timedelta(hours=1)).time()
        slots.append({'start': start_time.strftime('%H:%M'), 'end': end_time.strftime('%H:%M')})

    ocupados = (
        db.session.query(ReservationSlot)
        .join(Reservation)
        .filter(Reservation.court_id == court_id, Reservation.date == selected_date)
        .all()
    )
    occupied_set = set((o.start_time.strftime('%H:%M'), o.end_time.strftime('%H:%M')) for o in ocupados)

    result = []
    for slot in slots:
        ocupado = (slot['start'], slot['end']) in occupied_set
        result.append({
            'slot': f"{slot['start']}-{slot['end']}",
            'available': not ocupado
        })

    return jsonify({'hours': result})

# ------------------ Error 401 ------------------

@main_bp.app_errorhandler(401)
def unauthorized(error):
    return render_template('401.html'), 401

