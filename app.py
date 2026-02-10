from flask import Flask, render_template, request, jsonify, redirect, url_for, flash
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from datetime import datetime, timedelta
import os

from dotenv import load_dotenv

from models.user import User, db
from models.calendar import Event, Assignment
from models.edt import Course, Classroom, TimeSlot
from models.chat import Message, ChatRoom
from models.ai import AIChat
from models.homework import Homework, HomeworkSubmission
from models.notification import Notification

app = Flask(__name__)
load_dotenv()

# SECRET_KEY stable (required for sessions on deployed apps)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key')

# Database: Postgres via DATABASE_URL (Render), fallback SQLite for local dev
database_url = os.environ.get('DATABASE_URL')
if database_url:
    database_url = database_url.strip()
    # Render (and others) may give postgres://; SQLAlchemy expects postgresql://
    if database_url.startswith('postgres://'):
        database_url = database_url.replace('postgres://', 'postgresql://', 1)

    app.config['SQLALCHEMY_DATABASE_URI'] = database_url
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///agenda_scolaire.db'

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

app.config['UPLOAD_FOLDER'] = 'static/uploads'

db.init_app(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'


def _should_auto_init_db() -> bool:
    value = os.environ.get('AUTO_INIT_DB', 'true').strip().lower()
    return value in {'1', 'true', 'yes', 'y', 'on'}


def _should_seed_default_users() -> bool:
    value = os.environ.get('SEED_DEFAULT_USERS', 'false').strip().lower()
    return value in {'1', 'true', 'yes', 'y', 'on'}


def _init_db_if_needed() -> None:
    if not _should_auto_init_db():
        return

    with app.app_context():
        db.create_all()

        if _should_seed_default_users() and not User.query.first():
            admin = User(email='admin@planify.com', nom='Admin', prenom='PLANIFY', role='admin')
            admin.set_password('admin123')

            prof = User(email='prof@planify.com', nom='Martin', prenom='Sophie', role='professeur')
            prof.set_password('prof123')

            eleve = User(email='eleve@planify.com', nom='Dupont', prenom='Léo', role='eleve')
            eleve.set_password('eleve123')

            db.session.add_all([admin, prof, eleve])
            db.session.commit()


# Run optional initialization on import so it also works with `flask run`/WSGI.
_init_db_if_needed()

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Filtre personnalisé Jinja2 : nl2br (remplace les sauts de ligne par <br/>)
@app.template_filter('nl2br')
def nl2br(value):
    """Remplace les sauts de ligne par des balises <br/>"""
    if not value:
        return value
    return value.replace('\n', '<br/>')

# Routes d'authentification
@app.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = User.query.filter_by(email=email).first()
        
        if user and user.check_password(password):
            login_user(user)
            flash('Connexion réussie!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Email ou mot de passe incorrect', 'error')
    
    return render_template('auth/login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        nom = request.form['nom']
        prenom = request.form['prenom']
        role = request.form['role']
        
        if User.query.filter_by(email=email).first():
            flash('Email déjà utilisé', 'error')
            return redirect(url_for('register'))
        
        user = User(email=email, nom=nom, prenom=prenom, role=role)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        
        flash('Compte créé avec succès!', 'success')
        return redirect(url_for('login'))
    
    return render_template('auth/register.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

# Dashboard
@app.route('/dashboard')
@login_required
def dashboard():
    today = datetime.now().date()
    
    # Événements du jour
    events_today = Event.query.filter(
        Event.start_date >= today,
        Event.start_date < today + timedelta(days=1),
        Event.user_id == current_user.id
    ).all()
    
    # Devoirs à venir (seulement pour élèves et professeurs)
    upcoming_assignments = []
    if current_user.role in ['eleve', 'professeur']:
        upcoming_assignments = Assignment.query.filter(
            Assignment.due_date >= today,
            Assignment.user_id == current_user.id
        ).order_by(Assignment.due_date).limit(5).all()
    
    # Cours du jour
    today_courses = Course.query.join(TimeSlot).filter(
        TimeSlot.day_of_week == today.weekday()
    ).all()
    
    return render_template('index.html',
                         events_today=events_today,
                         assignments=upcoming_assignments,
                         courses_today=today_courses,
                         now=datetime.now())

# Calendrier
@app.route('/calendar')
@login_required
def calendar():
    view = request.args.get('view', 'month')
    date_str = request.args.get('date', datetime.now().strftime('%Y-%m-%d'))
    return render_template('calendar.html', view=view, current_date=date_str)

@app.route('/api/events')
@login_required
def get_events():
    # Récupérer tous les événements (visibles par tous pour le calendrier partagé)
    events = Event.query.all()
    
    events_data = []
    for event in events:
        events_data.append({
            'id': event.id,
            'title': event.title,
            'date': event.start_date.strftime('%Y-%m-%d'),
            'start_time': event.start_date.strftime('%H:%M'),
            'end_time': event.end_date.strftime('%H:%M') if event.end_date else None,
            'type': event.event_type,
            'description': event.description,
            'color': event.color,
            'user_id': event.user_id
        })
    
    return jsonify(events_data)

@app.route('/api/events/create', methods=['POST'])
@login_required
def create_event():
    # Seuls les admins et professeurs peuvent créer des événements
    if current_user.role not in ['admin', 'professeur']:
        return jsonify({'success': False, 'error': 'Non autorisé. Seuls les administrateurs et professeurs peuvent créer des événements.'}), 403
    
    data = request.get_json()
    
    try:
        # Gérer les heures de début et de fin
        start_datetime = datetime.strptime(data['date'] + ' ' + data['start_time'], '%Y-%m-%d %H:%M')
        end_datetime = None
        
        if data.get('end_time'):
            end_datetime = datetime.strptime(data['date'] + ' ' + data['end_time'], '%Y-%m-%d %H:%M')
            
            # Vérifier que l'heure de fin est après l'heure de début
            if end_datetime <= start_datetime:
                return jsonify({'success': False, 'error': 'L\'heure de fin doit être postérieure à l\'heure de début'}), 400
        
        event = Event(
            title=data['title'],
            start_date=start_datetime,
            end_date=end_datetime,
            event_type=data['type'],
            description=data.get('description', ''),
            user_id=current_user.id,
            color=data.get('color', '#6366f1')
        )
        
        db.session.add(event)
        db.session.commit()
        
        return jsonify({'success': True, 'event_id': event.id})
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/events/<int:event_id>/delete', methods=['DELETE'])
@login_required
def delete_event(event_id):
    # Seuls les admins et professeurs peuvent supprimer des événements
    if current_user.role not in ['admin', 'professeur']:
        return jsonify({'success': False, 'error': 'Non autorisé. Seuls les administrateurs et professeurs peuvent supprimer des événements.'}), 403
    
    try:
        event = Event.query.get_or_404(event_id)
        
        # Vérifier si l'utilisateur peut supprimer cet événement
        # Les admins peuvent supprimer tous les événements, les professeurs seulement les leurs
        if current_user.role == 'professeur' and event.user_id != current_user.id:
            return jsonify({'success': False, 'error': 'Vous ne pouvez supprimer que vos propres événements.'}), 403
        
        db.session.delete(event)
        db.session.commit()
        
        return jsonify({'success': True, 'message': 'Événement supprimé avec succès'})
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500

# EDT - Emploi du Temps
@app.route('/edt')
@login_required
def edt():
    days = ['Lundi', 'Mardi', 'Mercredi', 'Jeudi', 'Vendredi', 'Samedi', 'Dimanche']
    time_slots = [
        '07:00-08:00', '08:00-09:00', '09:00-10:00', '10:00-11:00', '11:00-12:00', 
        '12:00-13:00', '13:00-14:00', '14:00-15:00', '15:00-16:00', '16:00-17:00', 
        '17:00-18:00', '18:00-19:00'
    ]
    
    # Organiser par jour et créneau avec des données sérialisables
    schedule = {}
    schedule_json = {}
    for day_index, day_name in enumerate(days):
        schedule[day_name] = {}
        schedule_json[day_name] = {}
        for slot in time_slots:
            courses = Course.query.join(TimeSlot).filter(
                TimeSlot.day_of_week == day_index,
                TimeSlot.time_range == slot
            ).all()
            schedule[day_name][slot] = courses
            # Version JSON sérialisable
            schedule_json[day_name][slot] = [{
                'id': course.id,
                'name': course.name,
                'teacher': course.teacher.prenom + ' ' + course.teacher.nom if course.teacher else 'Non assigné',
                'classroom': course.classroom.name if course.classroom else 'Non assignée',
                'color': course.color or '#6366f1'
            } for course in courses]
    
    classrooms = Classroom.query.all()
    classrooms_json = [{
        'id': classroom.id,
        'name': classroom.name,
        'capacity': classroom.capacity,
        'location': classroom.location or 'Non spécifiée'
    } for classroom in classrooms]
    
    return render_template('edt.html',
                         schedule=schedule,
                         schedule_json=schedule_json,
                         days=days,
                         time_slots=time_slots,
                         classrooms=classrooms,
                         classrooms_json=classrooms_json)

@app.route('/api/courses/create', methods=['POST'])
@login_required
def create_course():
    if current_user.role not in ['admin', 'professeur']:
        return jsonify({'success': False, 'error': 'Non autorisé. Seuls les administrateurs et professeurs peuvent créer des cours.'}), 403
    
    data = request.get_json()
    
    try:
        # Créer le cours
        course = Course(
            name=data['name'],
            description=data.get('description', ''),
            color=data.get('color', '#6366f1'),
            teacher_id=data['teacher_id'],
            classroom_id=data['classroom_id']
        )
        db.session.add(course)
        db.session.flush()  # Pour obtenir l'ID
        
        # Créer le créneau horaire
        # Mapper le jour en index — accepter soit un index (0..6) envoyé par le front, soit un nom de jour
        day_mapping = {
            'Lundi': 0, 'Mardi': 1, 'Mercredi': 2,
            'Jeudi': 3, 'Vendredi': 4, 'Samedi': 5, 'Dimanche': 6
        }

        day_value = data.get('day')
        if isinstance(day_value, int) or (isinstance(day_value, str) and day_value.isdigit()):
            day_index = int(day_value)
        else:
            day_index = day_mapping.get(day_value, 0)

        timeslot = TimeSlot(
            course_id=course.id,
            day_of_week=day_index,
            time_range=data['slot']
        )
        db.session.add(timeslot)
        db.session.commit()
        
        return jsonify({'success': True, 'course_id': course.id})
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/classrooms')
@login_required
def classrooms():
    classrooms = Classroom.query.all()
    return render_template('classrooms.html', classrooms=classrooms)

# API pour la gestion des salles
@app.route('/api/classrooms', methods=['POST'])
@login_required
def create_classroom():
    """Créer une nouvelle salle (Admin et Professeur seulement)"""
    if current_user.role not in ['admin', 'professeur']:
        return jsonify({'success': False, 'message': 'Accès non autorisé'}), 403
    
    try:
        data = request.get_json()
        
        # Validation des données
        if not data.get('name') or not data.get('capacity'):
            return jsonify({'success': False, 'message': 'Nom et capacité requis'}), 400
        
        # Vérifier si une salle avec ce nom existe déjà
        existing = Classroom.query.filter_by(name=data['name']).first()
        if existing:
            return jsonify({'success': False, 'message': 'Une salle avec ce nom existe déjà'}), 400
        
        # Créer la nouvelle salle
        classroom = Classroom(
            name=data['name'],
            capacity=data['capacity'],
            equipment=data.get('equipment', '')
        )
        
        db.session.add(classroom)
        db.session.commit()
        
        return jsonify({'success': True, 'message': 'Salle créée avec succès'})
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/classrooms/<int:classroom_id>', methods=['PUT'])
@login_required
def update_classroom(classroom_id):
    """Modifier une salle existante (Admin et Professeur seulement)"""
    if current_user.role not in ['admin', 'professeur']:
        return jsonify({'success': False, 'message': 'Accès non autorisé'}), 403
    
    try:
        classroom = Classroom.query.get_or_404(classroom_id)
        data = request.get_json()
        
        # Validation des données
        if not data.get('name') or not data.get('capacity'):
            return jsonify({'success': False, 'message': 'Nom et capacité requis'}), 400
        
        # Vérifier si une autre salle avec ce nom existe déjà
        existing = Classroom.query.filter(
            Classroom.name == data['name'],
            Classroom.id != classroom_id
        ).first()
        if existing:
            return jsonify({'success': False, 'message': 'Une salle avec ce nom existe déjà'}), 400
        
        # Mettre à jour la salle
        classroom.name = data['name']
        classroom.capacity = data['capacity']
        classroom.equipment = data.get('equipment', '')
        
        db.session.commit()
        
        return jsonify({'success': True, 'message': 'Salle modifiée avec succès'})
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/classrooms/<int:classroom_id>', methods=['DELETE'])
@login_required
def delete_classroom(classroom_id):
    """Supprimer une salle (Admin seulement)"""
    if current_user.role != 'admin':
        return jsonify({'success': False, 'message': 'Seuls les administrateurs peuvent supprimer des salles'}), 403
    
    try:
        classroom = Classroom.query.get_or_404(classroom_id)
        
        # Vérifier si la salle est utilisée dans des cours
        courses_using_classroom = Course.query.filter_by(classroom_id=classroom_id).count()
        if courses_using_classroom > 0:
            return jsonify({
                'success': False, 
                'message': f'Impossible de supprimer la salle. Elle est utilisée par {courses_using_classroom} cours.'
            }), 400
        
        db.session.delete(classroom)
        db.session.commit()
        
        return jsonify({'success': True, 'message': 'Salle supprimée avec succès'})
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500

# Gestion des comptes (Admin uniquement)
@app.route('/admin/users')
@login_required
def admin_users():
    if current_user.role != 'admin':
        flash('Accès non autorisé.', 'error')
        return redirect(url_for('dashboard'))
    
    users = User.query.all()
    return render_template('admin/users.html', users=users)

@app.route('/api/admin/users', methods=['GET'])
@login_required
def get_users_api():
    if current_user.role != 'admin':
        return jsonify({'success': False, 'error': 'Non autorisé'}), 403
    
    users = User.query.all()
    users_data = []
    for user in users:
        users_data.append({
            'id': user.id,
            'nom': user.nom,
            'prenom': user.prenom,
            'email': user.email,
            'role': user.role,
            'is_active': user.is_active,
            'created_at': user.created_at.strftime('%d/%m/%Y')
        })
    
    return jsonify({'success': True, 'users': users_data})

@app.route('/api/admin/users/create', methods=['POST'])
@login_required
def create_user_api():
    if current_user.role != 'admin':
        return jsonify({'success': False, 'error': 'Non autorisé'}), 403
    
    try:
        data = request.get_json()
        
        # Vérifier si l'email existe déjà
        existing_user = User.query.filter_by(email=data['email']).first()
        if existing_user:
            return jsonify({'success': False, 'error': 'Un utilisateur avec cet email existe déjà'})
        
        # Créer le nouvel utilisateur
        new_user = User(
            nom=data['nom'],
            prenom=data['prenom'],
            email=data['email'],
            role=data['role']
        )
        new_user.set_password(data['password'])
        
        db.session.add(new_user)
        db.session.commit()
        
        return jsonify({'success': True, 'message': 'Utilisateur créé avec succès'})
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/admin/users/<int:user_id>/update', methods=['POST'])
@login_required
def update_user_api(user_id):
    if current_user.role != 'admin':
        return jsonify({'success': False, 'error': 'Non autorisé'}), 403
    
    try:
        user = User.query.get_or_404(user_id)
        data = request.get_json()
        
        # Vérifier si l'email est déjà utilisé par un autre utilisateur
        if data['email'] != user.email:
            existing_user = User.query.filter_by(email=data['email']).first()
            if existing_user:
                return jsonify({'success': False, 'error': 'Un utilisateur avec cet email existe déjà'})
        
        # Mettre à jour les données
        user.nom = data['nom']
        user.prenom = data['prenom']
        user.email = data['email']
        user.role = data['role']
        user.is_active = data['is_active']
        
        # Changer le mot de passe si fourni
        if data.get('password'):
            user.set_password(data['password'])
        
        db.session.commit()
        
        return jsonify({'success': True, 'message': 'Utilisateur mis à jour avec succès'})
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/admin/users/<int:user_id>/delete', methods=['POST'])
@login_required
def delete_user_api(user_id):
    if current_user.role != 'admin':
        return jsonify({'success': False, 'error': 'Non autorisé'}), 403
    
    try:
        user = User.query.get_or_404(user_id)
        
        # Empêcher la suppression de son propre compte
        if user.id == current_user.id:
            return jsonify({'success': False, 'error': 'Vous ne pouvez pas supprimer votre propre compte'})
        
        db.session.delete(user)
        db.session.commit()
        
        return jsonify({'success': True, 'message': 'Utilisateur supprimé avec succès'})
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)})

# Devoirs
@app.route('/homework')
@login_required
def homework():
    if current_user.role == 'eleve':
        # Vue élève : voir tous les devoirs assignés
        homework_list = Homework.query.filter_by(is_published=True).order_by(Homework.due_date.asc()).all()
        homework_data = [hw.to_dict(student_id=current_user.id) for hw in homework_list]
        return render_template('homework/student.html', homework=homework_data)
    
    elif current_user.role == 'professeur':
        # Vue professeur : voir ses devoirs créés
        homework_list = Homework.query.filter_by(teacher_id=current_user.id).order_by(Homework.created_at.desc()).all()
        homework_data = [hw.to_dict() for hw in homework_list]
        return render_template('homework/teacher.html', homework=homework_data)
    
    else:
        # Vue admin : voir tous les devoirs
        homework_list = Homework.query.order_by(Homework.created_at.desc()).all()
        homework_data = [hw.to_dict() for hw in homework_list]
        
        teachers = User.query.filter_by(role='professeur').all()
        subjects = list(set(hw.subject for hw in homework_list if hw.subject))
        
        total_submissions = sum(hw.submission_count for hw in homework_list)  
        graded_submissions = HomeworkSubmission.query.filter(HomeworkSubmission.grade.isnot(None)).count()
        
        return render_template('homework/admin.html', 
                             homework=homework_data, 
                             teachers=teachers, 
                             subjects=subjects,
                             total_submissions=total_submissions,
                             graded_submissions=graded_submissions)

@app.route('/homework/<int:homework_id>')
@login_required
def homework_detail(homework_id):
    homework = Homework.query.get_or_404(homework_id)
    
    if current_user.role == 'eleve':
        # Vérifier si l'élève peut voir ce devoir
        if not homework.is_published:
            flash('Ce devoir n\'est pas encore disponible.', 'error')
            return redirect(url_for('homework'))
        
        submission = homework.get_submission_for_student(current_user.id)
        # Utiliser le template unique `detail.html` existant (gère les vues élève/prof/admin)
        return render_template('homework/detail.html', homework=homework, student_submission=submission)
    
    elif current_user.role == 'professeur':
        # Vérifier si c'est le professeur qui a créé le devoir
        if homework.teacher_id != current_user.id:
            flash('Vous n\'avez pas accès à ce devoir.', 'error')
            return redirect(url_for('homework'))
        
        submissions = homework.submissions.all()
        return render_template('homework/detail.html', homework=homework, submissions=submissions)
    
    else:
        # Admin peut tout voir
        submissions = homework.submissions.all()
        return render_template('homework/detail.html', homework=homework, submissions=submissions)

@app.route('/api/homework/create', methods=['POST'])
@login_required
def create_homework():
    if current_user.role not in ['professeur', 'admin']:
        return jsonify({'success': False, 'error': 'Non autorisé'}), 403
    
    try:
        data = request.get_json()
        
        # Créer le nouveau devoir
        homework = Homework(
            title=data['title'],
            description=data['description'],
            due_date=datetime.fromisoformat(data['due_date'].replace('Z', '+00:00')),
            subject=data.get('subject', ''),
            points=int(data.get('points', 20)),
            is_published=data.get('is_published', True),
            teacher_id=current_user.id
        )
        
        db.session.add(homework)
        db.session.commit()
        
        # Créer des notifications pour tous les élèves si le devoir est publié
        if homework.is_published:
            students = User.query.filter_by(role='eleve').all()
            for student in students:
                Notification.create_homework_notification(student.id, homework)
            db.session.commit()
        
        return jsonify({'success': True, 'message': 'Devoir créé avec succès', 'homework_id': homework.id})
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/homework/<int:homework_id>/update', methods=['POST'])
@login_required
def update_homework(homework_id):
    homework = Homework.query.get_or_404(homework_id)
    
    # Vérifier les permissions
    if current_user.role == 'professeur' and homework.teacher_id != current_user.id:
        return jsonify({'success': False, 'error': 'Non autorisé'}), 403
    elif current_user.role not in ['professeur', 'admin']:
        return jsonify({'success': False, 'error': 'Non autorisé'}), 403
    
    try:
        data = request.get_json()
        
        homework.title = data.get('title', homework.title)
        homework.description = data.get('description', homework.description)
        homework.subject = data.get('subject', homework.subject)
        homework.points = int(data.get('points', homework.points))
        homework.is_published = data.get('is_published', homework.is_published)
        
        if data.get('due_date'):
            homework.due_date = datetime.fromisoformat(data['due_date'].replace('Z', '+00:00'))
        
        homework.updated_at = datetime.utcnow()
        
        db.session.commit()
        
        return jsonify({'success': True, 'message': 'Devoir mis à jour avec succès'})
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/homework/<int:homework_id>/delete', methods=['POST'])
@login_required
def delete_homework(homework_id):
    homework = Homework.query.get_or_404(homework_id)
    
    # Vérifier les permissions
    if current_user.role == 'professeur' and homework.teacher_id != current_user.id:
        return jsonify({'success': False, 'error': 'Non autorisé'}), 403
    elif current_user.role not in ['professeur', 'admin']:
        return jsonify({'success': False, 'error': 'Non autorisé'}), 403
    
    try:
        db.session.delete(homework)
        db.session.commit()
        
        return jsonify({'success': True, 'message': 'Devoir supprimé avec succès'})
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/homework/<int:homework_id>/submit', methods=['POST'])
@login_required
def submit_homework(homework_id):
    if current_user.role != 'eleve':
        return jsonify({'success': False, 'error': 'Seuls les élèves peuvent soumettre des devoirs'}), 403
    
    homework = Homework.query.get_or_404(homework_id)
    
    if not homework.is_published:
        return jsonify({'success': False, 'error': 'Ce devoir n\'est pas encore disponible'}), 403
    
    try:
        data = request.get_json()
        
        # Vérifier si une soumission existe déjà
        existing_submission = homework.get_submission_for_student(current_user.id)
        
        if existing_submission:
            # Mettre à jour la soumission existante
            existing_submission.content = data.get('content', '')
            existing_submission.submitted_at = datetime.utcnow()
            existing_submission.status = 'late' if homework.is_overdue() else 'submitted'
            db.session.commit()
            
            return jsonify({'success': True, 'message': 'Devoir mis à jour avec succès'})
        else:
            # Créer une nouvelle soumission
            submission = HomeworkSubmission(
                homework_id=homework_id,
                student_id=current_user.id,
                content=data.get('content', ''),
                status='late' if homework.is_overdue() else 'submitted'
            )
            
            db.session.add(submission)
            db.session.commit()
            
            return jsonify({'success': True, 'message': 'Devoir soumis avec succès'})
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/homework/submission/<int:submission_id>/grade', methods=['POST'])
@login_required
def grade_submission(submission_id):
    if current_user.role not in ['professeur', 'admin']:
        return jsonify({'success': False, 'error': 'Non autorisé'}), 403
    
    submission = HomeworkSubmission.query.get_or_404(submission_id)
    
    # Vérifier si c'est le professeur qui a créé le devoir
    if current_user.role == 'professeur' and submission.homework.teacher_id != current_user.id:
        return jsonify({'success': False, 'error': 'Non autorisé'}), 403
    
    try:
        data = request.get_json()
        
        submission.grade = float(data.get('grade', 0))
        submission.feedback = data.get('feedback', '')
        submission.status = 'graded'
        submission.graded_at = datetime.utcnow()
        
        # Créer une notification pour l'élève
        Notification.create_grade_notification(
            submission.student_id, 
            submission.homework, 
            submission.grade
        )
        
        db.session.commit()
        
        return jsonify({'success': True, 'message': 'Note attribuée avec succès'})
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)})

# Chat
@app.route('/chat')
@login_required
def chat_inbox():
    # Conversations de l'utilisateur avec jointure explicite
    user_chats = db.session.query(ChatRoom).filter(
        (ChatRoom.user1_id == current_user.id) | 
        (ChatRoom.user2_id == current_user.id)
    ).all()
    
    conversations = []
    for chat in user_chats:
        # Obtenir l'autre utilisateur en utilisant une requête directe
        if chat.user1_id == current_user.id:
            other_user = User.query.get(chat.user2_id)
        else:
            other_user = User.query.get(chat.user1_id)
            
        last_message = Message.query.filter_by(chat_id=chat.id).order_by(Message.created_at.desc()).first()
        unread_count = Message.query.filter_by(chat_id=chat.id, read=False).filter(Message.sender_id != current_user.id).count()
        
        conversations.append({
            'chat': chat,
            'other_user': other_user,
            'last_message': last_message,
            'unread_count': unread_count
        })
    
    # Liste des utilisateurs pour nouveau chat
    users = User.query.filter(User.id != current_user.id).all()
    
    return render_template('inbox.html',
                         conversations=conversations,
                         users=users)

@app.route('/chat/<int:chat_id>')
@login_required
def chat_room(chat_id):
    chat = ChatRoom.query.get_or_404(chat_id)
    
    # Vérifier que l'utilisateur peut accéder à ce canal
    if not chat.can_user_access(current_user.id, current_user.role):
        flash('Accès non autorisé', 'error')
        return redirect(url_for('chat_inbox'))
    
    other_user = chat.user2 if chat.user1_id == current_user.id else chat.user1
    
    # Marquer les messages comme lus
    Message.query.filter_by(chat_id=chat_id, read=False).filter(Message.sender_id != current_user.id).update({'read': True})
    db.session.commit()
    
    # Récupérer tous les messages et filtrer selon les règles de visibilité
    all_messages = Message.query.filter_by(chat_id=chat_id).order_by(Message.created_at.asc()).all()
    visible_messages = []
    
    for message in all_messages:
        if chat.is_message_visible_to_user(message, current_user.id, current_user.role):
            visible_messages.append(message)
    
    return render_template('chat_room.html',
                         chat=chat,
                         other_user=other_user,
                         messages=visible_messages)

@app.route('/api/chat/send', methods=['POST'])
@login_required
def send_message():
    data = request.get_json()
    chat_id = data.get('chat_id')
    content = data.get('content')
    
    if not content or not chat_id:
        return jsonify({'error': 'Données manquantes'}), 400
    
    message = Message(
        chat_id=chat_id,
        sender_id=current_user.id,
        content=content
    )
    
    db.session.add(message)
    db.session.commit()
    
    return jsonify({
        'success': True,
        'message': {
            'id': message.id,
            'content': message.content,
            'sender_id': message.sender_id,
            'created_at': message.created_at.isoformat(),
            'is_me': True
        }
    })

@app.route('/api/chat/<int:chat_id>/messages')
@login_required
def get_chat_messages(chat_id):
    messages = Message.query.filter_by(chat_id=chat_id).order_by(Message.created_at.asc()).all()
    
    messages_data = []
    for msg in messages:
        messages_data.append({
            'id': msg.id,
            'content': msg.content,
            'sender_id': msg.sender_id,
            'is_me': msg.sender_id == current_user.id,
            'created_at': msg.created_at.strftime('%H:%M'),
            'date': msg.created_at.strftime('%d/%m/%Y')
        })
    
    return jsonify(messages_data)

@app.route('/api/chat/start', methods=['POST'])
@login_required
def start_chat():
    data = request.get_json()
    other_user_id = data.get('user_id')
    
    # Récupérer l'autre utilisateur pour déterminer le type de canal
    other_user = User.query.get_or_404(other_user_id)
    
    # Vérifier si une conversation existe déjà
    existing_chat = ChatRoom.query.filter(
        ((ChatRoom.user1_id == current_user.id) & (ChatRoom.user2_id == other_user_id)) |
        ((ChatRoom.user1_id == other_user_id) & (ChatRoom.user2_id == current_user.id))
    ).first()
    
    if existing_chat:
        return jsonify({'chat_id': existing_chat.id})
    
    # Déterminer le type de canal selon les rôles
    channel_type = ChatRoom.get_channel_type(current_user.role, other_user.role)
    
    # Créer nouvelle conversation avec le type de canal approprié
    new_chat = ChatRoom(
        user1_id=current_user.id, 
        user2_id=other_user_id,
        channel_type=channel_type
    )
    db.session.add(new_chat)
    db.session.commit()
    
    return jsonify({'chat_id': new_chat.id})

# Assistant IA
@app.route('/ai/chat')
@login_required
def ai_chat():
    return render_template('ai.html', now=datetime.now())

@app.route('/ai/quiz')
@login_required
def ai_quiz():
    return render_template('ai_quiz.html', now=datetime.now())

@app.route('/api/ai/chat', methods=['POST'])
@login_required
def ai_chat_message():
    data = request.get_json()
    user_message = data.get('message')
    user_role = current_user.role
    
    # Réponses adaptées selon le rôle
    if user_role == 'admin':
        responses = [
            "🛠️ En tant qu'administrateur, concernant '{}', je vous recommande d'analyser les données de gestion...",
            "📊 Pour votre demande sur '{}', voici une approche administrative stratégique...",
            "🎯 D'un point de vue gestionnaire sur '{}', vous devriez considérer l'impact organisationnel...",
            "📈 Votre question sur '{}' nécessite une vision d'ensemble. Analysons les KPIs..."
        ]
    elif user_role == 'professeur':
        responses = [
            "👨‍🏫 En tant qu'enseignant, pour '{}', je suggère une approche pédagogique adaptée...",
            "📚 Concernant votre question sur '{}', voici comment l'intégrer dans votre cours...",
            "🎓 Pour '{}', considérez ces méthodes d'enseignement efficaces...",
            "📝 Votre demande sur '{}' peut être transformée en activité d'apprentissage..."
        ]
    else:  # élève
        responses = [
            "🎓 Excellente question ! Pour '{}', commençons par les bases...",
            "📖 Je vais t'expliquer '{}' de manière simple et claire...",
            "💡 Concernant '{}', voici une méthode pour mieux comprendre...",
            "📚 Ta question sur '{}' montre ton intérêt ! Voici comment l'aborder..."
        ]
    
    import random
    response_template = random.choice(responses)
    message_preview = user_message[:50] + '...' if len(user_message) > 50 else user_message
    ai_response = response_template.format(message_preview)
    
    # Ajouter des conseils spécifiques selon le rôle
    if user_role == 'admin':
        ai_response += "\n\n💼 Conseil admin : N'hésitez pas à consulter les rapports détaillés dans la section analyse."
    elif user_role == 'professeur':
        ai_response += "\n\n👩‍🏫 conseil prof : Pensez à adapter le contenu au niveau de vos élèves."
    else:
        ai_response += "\n\n🎯 Conseil : N'hésite pas à poser des questions de suivi pour approfondir !"
    
    # Sauvegarder la conversation
    chat = AIChat(
        user_id=current_user.id,
        user_message=user_message,
        ai_response=ai_response
    )
    db.session.add(chat)
    db.session.commit()
    
    return jsonify({
        'response': ai_response,
        'timestamp': datetime.now().isoformat()
    })

@app.route('/api/ai/suggestions', methods=['GET'])
@login_required
def ai_suggestions():
    """Retourne des suggestions contextuelles selon le rôle de l'utilisateur"""
    user_role = current_user.role
    
    # Interface propre sans suggestions prédéfinies
    suggestions = []
    
    return jsonify({
        'suggestions': suggestions,
        'role': user_role
    })

# Routes pour les notifications
@app.route('/api/notifications')
@login_required
def get_notifications():
    """Récupérer les notifications de l'utilisateur connecté"""
    notifications = Notification.query.filter_by(user_id=current_user.id)\
                                    .order_by(Notification.created_at.desc())\
                                    .limit(50).all()
    
    return jsonify({
        'notifications': [notif.to_dict() for notif in notifications],
        'unread_count': len([n for n in notifications if not n.is_read])
    })

@app.route('/api/notifications/<int:notification_id>/read', methods=['POST'])
@login_required
def mark_notification_read(notification_id):
    """Marquer une notification comme lue"""
    notification = Notification.query.filter_by(id=notification_id, user_id=current_user.id).first()
    if notification:
        notification.mark_as_read()
        return jsonify({'success': True})
    return jsonify({'success': False, 'error': 'Notification non trouvée'})

@app.route('/api/notifications/mark-all-read', methods=['POST'])
@login_required
def mark_all_notifications_read():
    """Marquer toutes les notifications comme lues"""
    notifications = Notification.query.filter_by(user_id=current_user.id, is_read=False).all()
    for notification in notifications:
        notification.is_read = True
    db.session.commit()
    return jsonify({'success': True})

@app.route('/notifications')  
@login_required
def notifications_page():
    """Page des notifications pour les élèves"""
    if current_user.role != 'eleve':
        return redirect(url_for('dashboard'))
    return render_template('notifications_page.html')

# Routes pour les paramètres de profil
@app.route('/settings')
@login_required
def settings():
    """Page des paramètres utilisateur"""
    return render_template('settings.html')

@app.route('/api/profile/update', methods=['POST'])
@login_required
def update_profile():
    """Mettre à jour les informations de profil"""
    try:
        data = request.get_json()
        
        # Vérifier si l'email est déjà utilisé par un autre utilisateur
        if data.get('email') != current_user.email:
            existing_user = User.query.filter_by(email=data['email']).first()
            if existing_user:
                return jsonify({'success': False, 'error': 'Cet email est déjà utilisé'})
        
        # Mettre à jour les champs
        current_user.prenom = data.get('prenom', current_user.prenom)
        current_user.nom = data.get('nom', current_user.nom)
        current_user.email = data.get('email', current_user.email)
        current_user.bio = data.get('bio', current_user.bio)
        current_user.phone = data.get('phone', current_user.phone)
        
        # Gérer la date de naissance
        if data.get('birth_date'):
            from datetime import datetime
            current_user.birth_date = datetime.strptime(data['birth_date'], '%Y-%m-%d').date()
        
        db.session.commit()
        return jsonify({'success': True, 'message': 'Profil mis à jour avec succès'})
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/profile/change-password', methods=['POST'])
@login_required
def change_password():
    """Changer le mot de passe"""
    try:
        data = request.get_json()
        
        # Vérifier le mot de passe actuel
        if not current_user.check_password(data['current_password']):
            return jsonify({'success': False, 'error': 'Mot de passe actuel incorrect'})
        
        # Mettre à jour le mot de passe
        current_user.set_password(data['new_password'])
        db.session.commit()
        
        return jsonify({'success': True, 'message': 'Mot de passe changé avec succès'})
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/profile/preferences', methods=['POST'])
@login_required
def update_preferences():
    """Mettre à jour les préférences"""
    try:
        data = request.get_json()
        
        current_user.email_notifications = data.get('email_notifications', False)
        current_user.homework_reminders = data.get('homework_reminders', False)
        current_user.theme = data.get('theme', 'light')
        current_user.language = data.get('language', 'fr')
        
        db.session.commit()
        return jsonify({'success': True, 'message': 'Préférences mises à jour'})
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/profile/upload-photo', methods=['POST'])
@login_required
def upload_profile_photo():
    """Upload de photo de profil"""
    try:
        if 'photo' not in request.files:
            return jsonify({'success': False, 'error': 'Aucune photo sélectionnée'})
        
        file = request.files['photo']
        if file.filename == '':
            return jsonify({'success': False, 'error': 'Aucune photo sélectionnée'})
        
        # Vérifier le type de fichier
        allowed_extensions = {'png', 'jpg', 'jpeg', 'gif'}
        if not ('.' in file.filename and file.filename.rsplit('.', 1)[1].lower() in allowed_extensions):
            return jsonify({'success': False, 'error': 'Type de fichier non autorisé'})
        
        # Créer le dossier uploads si nécessaire
        import os
        upload_folder = os.path.join('static', 'uploads', 'profiles')
        os.makedirs(upload_folder, exist_ok=True)
        
        # Supprimer l'ancienne photo
        if current_user.profile_photo:
            old_photo_path = os.path.join(upload_folder, current_user.profile_photo)
            if os.path.exists(old_photo_path):
                os.remove(old_photo_path)
        
        # Générer un nom unique pour le fichier
        import uuid
        filename = f"{current_user.id}_{uuid.uuid4().hex[:8]}.{file.filename.rsplit('.', 1)[1].lower()}"
        file_path = os.path.join(upload_folder, filename)
        
        # Sauvegarder le fichier
        file.save(file_path)
        
        # Mettre à jour la base de données
        current_user.profile_photo = filename
        db.session.commit()
        
        return jsonify({
            'success': True, 
            'message': 'Photo uploadée avec succès',
            'photo_url': f"/static/uploads/profiles/{filename}"
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/profile/remove-photo', methods=['POST'])
@login_required
def remove_profile_photo():
    """Supprimer la photo de profil"""
    try:
        if current_user.profile_photo:
            # Supprimer le fichier
            import os
            photo_path = os.path.join('static', 'uploads', 'profiles', current_user.profile_photo)
            if os.path.exists(photo_path):
                os.remove(photo_path)
            
            # Mettre à jour la base de données
            current_user.profile_photo = None
            db.session.commit()
        
        return jsonify({'success': True, 'message': 'Photo supprimée avec succès'})
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)})

if __name__ == '__main__':
    _init_db_if_needed()
    app.run(debug=True, host='0.0.0.0', port=5000)