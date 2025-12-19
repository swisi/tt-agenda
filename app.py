from flask import Flask, render_template, request, redirect, url_for, jsonify, session, flash
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta
from functools import wraps
import json

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///trainings.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'your-secret-key-change-this-in-production'
db = SQLAlchemy(app)

class Training(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    weekday = db.Column(db.Integer, nullable=False)
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=False)
    start_time = db.Column(db.Time, nullable=False)
    activities = db.relationship('Activity', backref='training', lazy=True, cascade='all, delete-orphan')

class Activity(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    training_id = db.Column(db.Integer, db.ForeignKey('training.id'), nullable=False)
    activity_type = db.Column(db.String(20), nullable=False)
    start_time = db.Column(db.Time, nullable=False)
    duration = db.Column(db.Integer, nullable=False)
    position_groups = db.Column(db.String(500), nullable=False)
    topic = db.Column(db.String(200))
    order_index = db.Column(db.Integer, default=0)
    topics_json = db.Column(db.Text)
    color = db.Column(db.String(7), default='#10b981')  # Standard: grün

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
    role = db.Column(db.String(20), default='user')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

WEEKDAYS = ['Montag', 'Dienstag', 'Mittwoch', 'Donnerstag', 'Freitag', 'Samstag', 'Sonntag']
POSITION_GROUPS = ['OL', 'DL', 'LB', 'DB', 'RB', 'TE', 'WR', 'QB']

# Importiere Farbkonfiguration
try:
    from activity_colors import get_activity_color, get_all_colors, LIGHT_MODE_COLORS, DARK_MODE_COLORS
except ImportError:
    # Fallback falls activity_colors.py nicht existiert
    LIGHT_MODE_COLORS = {'team': '#A8D5E2', 'prepractice': '#FFD6CC', 'individual': '#D4E4C5', 'group': '#FFE5B4'}
    DARK_MODE_COLORS = {'team': '#4A90A4', 'prepractice': '#C97A6B', 'individual': '#7A9B6B', 'group': '#C9A86B'}
    def get_activity_color(activity_type, theme='light'):
        color_map = DARK_MODE_COLORS if theme == 'dark' else LIGHT_MODE_COLORS
        return color_map.get(activity_type, '#E8E8E8' if theme == 'light' else '#4A4A4A')
    def get_all_colors(theme='light'):
        return DARK_MODE_COLORS.copy() if theme == 'dark' else LIGHT_MODE_COLORS.copy()

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Bitte melden Sie sich an.', 'warning')
            return redirect(url_for('login', next=request.url))
        return f(*args, **kwargs)
    return decorated_function

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Bitte melden Sie sich an.', 'warning')
            return redirect(url_for('login', next=request.url))
        if session.get('user_role') != 'admin':
            flash('Sie haben keine Berechtigung für diese Aktion.', 'danger')
            return redirect(url_for('index'))
        return f(*args, **kwargs)
    return decorated_function

@app.context_processor
def inject_colors():
    """Macht Farbkonfiguration und Hilfsfunktionen in allen Templates verfügbar."""
    return {
        'LIGHT_MODE_COLORS': LIGHT_MODE_COLORS,
        'DARK_MODE_COLORS': DARK_MODE_COLORS,
        'get_activity_color': get_activity_color,
        'timedelta': timedelta
    }

@app.route('/')
@login_required
def index():
    trainings = Training.query.all()
    
    # Finde aktuelles oder kommendes Training für heute
    now = datetime.now()
    today = now.date()
    current_time = now.time()
    today_weekday = today.weekday()  # 0=Montag, 6=Sonntag
    
    current_training = None
    current_activity = None
    next_activity = None
    training_status = None  # 'running', 'upcoming', 'finished'
    
    # Suche alle Trainings, die heute stattfinden könnten
    for training in trainings:
        # Prüfe ob heute der richtige Wochentag ist und das Datum im Bereich liegt
        if training.weekday == today_weekday and training.start_date <= today <= training.end_date:
            # Hole alle Aktivitäten für dieses Training
            activities = Activity.query.filter_by(training_id=training.id).order_by(Activity.order_index).all()
            
            if not activities:
                continue
            
            # Berechne Start- und Endzeit des gesamten Trainings
            first_activity = activities[0]
            last_activity = activities[-1]
            
            training_start = first_activity.start_time
            # Berechne Endzeit der letzten Aktivität
            last_end_datetime = datetime.combine(today, last_activity.start_time) + timedelta(minutes=last_activity.duration)
            training_end = last_end_datetime.time()
            
            # Prüfe ob Training noch nicht gestartet hat
            if current_time < training_start:
                if current_training is None or training_start < current_training.start_time:
                    current_training = training
                    training_status = 'upcoming'
                    next_activity = first_activity
                    current_activity = None
            # Prüfe ob Training gerade läuft
            elif current_time < training_end:
                current_training = training
                training_status = 'running'
                
                # Finde die aktuelle und nächste Aktivität
                for i, activity in enumerate(activities):
                    activity_end_datetime = datetime.combine(today, activity.start_time) + timedelta(minutes=activity.duration)
                    activity_end = activity_end_datetime.time()
                    
                    if activity.start_time <= current_time < activity_end:
                        current_activity = activity
                        if i + 1 < len(activities):
                            next_activity = activities[i + 1]
                        break
                    elif current_time < activity.start_time:
                        next_activity = activity
                        break
                
                break  # Wir haben ein laufendes Training gefunden, keine weiteren prüfen
    
    return render_template('index.html', 
                         trainings=trainings, 
                         weekdays=WEEKDAYS,
                         current_training=current_training,
                         current_activity=current_activity,
                         next_activity=next_activity,
                         training_status=training_status,
                         now=now)

@app.route('/test')
def test():
    """Test-Route ohne Login-Schutz"""
    return '<h1>Flask funktioniert!</h1><p>Gehe zu <a href="/login">/login</a></p>'

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()

        if user and user.check_password(password):
            session['user_id'] = user.id
            session['username'] = user.username
            session['user_role'] = user.role
            flash('Erfolgreich angemeldet!', 'success')
            next_page = request.args.get('next')
            return redirect(next_page or url_for('index'))
        else:
            flash('Ungültiger Benutzername oder Passwort.', 'danger')

    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    flash('Sie wurden abgemeldet.', 'info')
    return redirect(url_for('login'))

@app.route('/training/new', methods=['GET', 'POST'])
@admin_required
def new_training():
    if request.method == 'POST':
        training = Training(
            name=request.form['name'],
            weekday=int(request.form['weekday']),
            start_date=datetime.strptime(request.form['start_date'], '%Y-%m-%d').date(),
            end_date=datetime.strptime(request.form['end_date'], '%Y-%m-%d').date(),
            start_time=datetime.strptime(request.form['start_time'], '%H:%M').time()
        )
        db.session.add(training)
        db.session.commit()
        flash('Training erfolgreich erstellt!', 'success')
        return redirect(url_for('edit_training', id=training.id))
    return render_template('training_form.html', weekdays=WEEKDAYS)

@app.route('/training/<int:id>/edit', methods=['GET', 'POST'])
@admin_required
def edit_training(id):
    training = Training.query.get_or_404(id)
    if request.method == 'POST':
        training.name = request.form['name']
        training.weekday = int(request.form['weekday'])
        training.start_date = datetime.strptime(request.form['start_date'], '%Y-%m-%d').date()
        training.end_date = datetime.strptime(request.form['end_date'], '%Y-%m-%d').date()
        training.start_time = datetime.strptime(request.form['start_time'], '%H:%M').time()
        db.session.commit()
        flash('Training erfolgreich aktualisiert!', 'success')
        return redirect(url_for('edit_training', id=id))
    activities = Activity.query.filter_by(training_id=id).order_by(Activity.order_index).all()
    activities_json = [{
        'id': a.id,
        'activity_type': a.activity_type,
        'duration': a.duration,
        'position_groups': a.position_groups,
        'topic': a.topic,
        'topics_json': a.topics_json,
        'color': a.color if hasattr(a, 'color') and a.color else get_activity_color(a.activity_type, 'light')
    } for a in activities]
    return render_template('training_edit.html', training=training, activities=activities, activities_json=json.dumps(activities_json), weekdays=WEEKDAYS, position_groups=POSITION_GROUPS)

@app.route('/training/<int:id>/delete', methods=['POST'])
@admin_required
def delete_training(id):
    training = Training.query.get_or_404(id)
    db.session.delete(training)
    db.session.commit()
    flash('Training erfolgreich gelöscht!', 'success')
    return redirect(url_for('index'))

@app.route('/activity/add', methods=['GET', 'POST'])
@admin_required
def add_activity():
    training_id = request.args.get('training_id') or (request.form.get('training_id') if request.method == 'POST' else None)
    if not training_id:
        flash('Training-ID fehlt', 'error')
        return redirect(url_for('index'))
    
    training = Training.query.get_or_404(training_id)
    
    if request.method == 'POST':
        # Form-Submission verarbeiten
        activity_type = request.form.get('activity_type')
        duration = int(request.form.get('duration', 60))
        # Farbe wird automatisch basierend auf Typ zugewiesen (Light-Mode als Standard)
        color = get_activity_color(activity_type, 'light')
        
        max_order = db.session.query(db.func.max(Activity.order_index)).filter_by(training_id=training_id).scalar() or -1

        if max_order == -1:
            if activity_type == 'prepractice':
                start_datetime = datetime.combine(datetime.today(), training.start_time)
                start_datetime -= timedelta(minutes=duration)
                start_time = start_datetime.time()
            else:
                start_time = training.start_time
        else:
            last_activity = Activity.query.filter_by(training_id=training_id).order_by(Activity.order_index.desc()).first()
            start_datetime = datetime.combine(datetime.today(), last_activity.start_time)
            start_datetime += timedelta(minutes=last_activity.duration)
            start_time = start_datetime.time()

        topics_json = None
        position_groups = []
        
        if activity_type in ['team', 'prepractice']:
            position_groups = POSITION_GROUPS
            topic = request.form.get('topic', '')
        elif activity_type == 'individual':
            position_groups = POSITION_GROUPS
            mode = request.form.get('individual_mode', 'same')
            topics_per_group = {}
            if mode == 'same':
                common_topic = request.form.get('individual_common_topic', '')
                for group in POSITION_GROUPS:
                    topics_per_group[group] = common_topic
            else:
                for group in POSITION_GROUPS:
                    topics_per_group[group] = request.form.get(f'individual_topic_{group}', '')
            topics_json = json.dumps(topics_per_group)
            topic = None
        elif activity_type == 'group':
            # Parse group combinations - durchsuche alle möglichen Indizes
            combinations = []
            all_selected_groups = set()
            i = 0
            max_iterations = 100
            found_any = False
            
            while i < max_iterations:
                combo_groups = request.form.getlist(f'combo_{i}_groups')
                combo_topic = request.form.get(f'combo_{i}_topic', '').strip()
                
                # Wenn keine Gruppen UND kein Topic gefunden werden, prüfe ob wir fertig sind
                if not combo_groups and not combo_topic:
                    # Wenn wir schon Kombinationen gefunden haben, sind wir wahrscheinlich fertig
                    if found_any:
                        break
                    # Sonst könnte es eine Lücke sein, weiter suchen
                    i += 1
                    continue
                
                found_any = True
                
                # Nur hinzufügen wenn sowohl Gruppen als auch Topic vorhanden sind
                if combo_groups and combo_topic:
                    combinations.append({'groups': combo_groups, 'topic': combo_topic})
                    all_selected_groups.update(combo_groups)
                elif combo_groups and not combo_topic:
                    # Gruppen vorhanden aber kein Topic - überspringen (unvollständig)
                    pass
                elif not combo_groups and combo_topic:
                    # Topic vorhanden aber keine Gruppen - überspringen (unvollständig)
                    pass
                
                i += 1
            
            position_groups = list(all_selected_groups) if all_selected_groups else []
            topics_json = json.dumps(combinations) if combinations else None
            topic = None

        activity = Activity(
            training_id=training_id,
            activity_type=activity_type,
            start_time=start_time,
            duration=duration,
            position_groups=json.dumps(position_groups),
            topic=topic,
            order_index=max_order + 1,
            topics_json=topics_json,
            color=color
        )
        db.session.add(activity)
        db.session.commit()

        recalculate_times(training_id)
        flash('Aktivität erfolgreich hinzugefügt!', 'success')
        return redirect(url_for('edit_training', id=training_id))
    
    # GET: Formular anzeigen
    return render_template('activity_form.html', training=training, activity=None, position_groups=POSITION_GROUPS, individual_mode_same=True, individual_common_topic='', individual_topics={})

@app.route('/activity/add_old', methods=['POST'])
@admin_required
def add_activity_old():
    data = request.json
    training = Training.query.get_or_404(data['training_id'])

    max_order = db.session.query(db.func.max(Activity.order_index)).filter_by(training_id=data['training_id']).scalar() or -1

    if max_order == -1:
        if data['activity_type'] == 'prepractice':
            start_datetime = datetime.combine(datetime.today(), training.start_time)
            start_datetime -= timedelta(minutes=int(data['duration']))
            start_time = start_datetime.time()
        else:
            start_time = training.start_time
    else:
        last_activity = Activity.query.filter_by(training_id=data['training_id']).order_by(Activity.order_index.desc()).first()
        start_datetime = datetime.combine(datetime.today(), last_activity.start_time)
        start_datetime += timedelta(minutes=last_activity.duration)
        start_time = start_datetime.time()

    topics_json = None
    if data['activity_type'] == 'individual':
        topics_json = json.dumps(data.get('topics_per_group', {}))
    elif data['activity_type'] == 'group':
        topics_json = json.dumps(data.get('group_combinations', []))

    activity = Activity(
        training_id=data['training_id'],
        activity_type=data['activity_type'],
        start_time=start_time,
        duration=int(data['duration']),
        position_groups=json.dumps(data['position_groups']),
        topic=data.get('topic', ''),
        order_index=max_order + 1,
        topics_json=topics_json,
        color=data.get('color', '#10b981')
    )
    db.session.add(activity)
    db.session.commit()

    recalculate_times(data['training_id'])

    return jsonify({'id': activity.id, 'success': True})

@app.route('/activity/<int:id>/edit', methods=['GET', 'POST'])
@admin_required
def edit_activity(id):
    activity = Activity.query.get_or_404(id)
    training = activity.training
    
    # Berechne ob Individual-Mode "same" ist und bereite Topics-Dict vor
    individual_mode_same = True
    individual_common_topic = ''
    individual_topics = {}
    if activity and activity.activity_type == 'individual' and activity.topics_json:
        try:
            topics = json.loads(activity.topics_json)
            if isinstance(topics, dict):
                individual_topics = topics
                topic_values = list(topics.values())
                if topic_values:
                    first_topic = topic_values[0]
                    individual_mode_same = all(t == first_topic for t in topic_values)
                    individual_common_topic = first_topic if individual_mode_same else ''
        except:
            pass
    
    if request.method == 'POST':
        activity_type = request.form.get('activity_type')
        duration = int(request.form.get('duration', 60))
        color = request.form.get('color', '#10b981')
        
        topics_json = None
        position_groups = []
        
        if activity_type in ['team', 'prepractice']:
            position_groups = POSITION_GROUPS
            activity.topic = request.form.get('topic', '')
        elif activity_type == 'individual':
            position_groups = POSITION_GROUPS
            mode = request.form.get('individual_mode', 'same')
            topics_per_group = {}
            if mode == 'same':
                common_topic = request.form.get('individual_common_topic', '')
                for group in POSITION_GROUPS:
                    topics_per_group[group] = common_topic
            else:
                for group in POSITION_GROUPS:
                    topics_per_group[group] = request.form.get(f'individual_topic_{group}', '')
            topics_json = json.dumps(topics_per_group)
            activity.topic = None
        elif activity_type == 'group':
            combinations = []
            all_selected_groups = set()
            # Iteriere durch alle möglichen Kombinationen (bis keine mehr gefunden werden)
            # Verwende combo_count als Hinweis, aber durchsuche auch darüber hinaus für Sicherheit
            combo_count = int(request.form.get('combo_count', 0))
            max_iterations = max(combo_count + 5, 100)  # Suche etwas weiter als combo_count
            found_any = False
            
            i = 0
            while i < max_iterations:
                combo_groups = request.form.getlist(f'combo_{i}_groups')
                combo_topic = request.form.get(f'combo_{i}_topic', '').strip()
                
                # Debug: Ausgabe für Entwicklung
                # print(f"Combo {i}: groups={combo_groups}, topic='{combo_topic}'")
                
                # Wenn keine Gruppen UND kein Topic gefunden werden, prüfe ob wir fertig sind
                if not combo_groups and not combo_topic:
                    # Wenn wir schon Kombinationen gefunden haben UND über combo_count hinaus sind, sind wir fertig
                    if found_any and i >= combo_count:
                        break
                    # Sonst könnte es eine Lücke sein, weiter suchen
                    i += 1
                    continue
                
                found_any = True
                
                # Nur hinzufügen wenn sowohl Gruppen als auch Topic vorhanden sind
                if combo_groups and combo_topic:
                    combinations.append({'groups': combo_groups, 'topic': combo_topic})
                    all_selected_groups.update(combo_groups)
                elif combo_groups and not combo_topic:
                    # Gruppen vorhanden aber kein Topic - überspringen (unvollständig)
                    pass
                elif not combo_groups and combo_topic:
                    # Topic vorhanden aber keine Gruppen - überspringen (unvollständig)
                    pass
                
                i += 1
            
            position_groups = list(all_selected_groups) if all_selected_groups else []
            topics_json = json.dumps(combinations) if combinations else None
            activity.topic = None

        activity.activity_type = activity_type
        activity.duration = duration
        activity.position_groups = json.dumps(position_groups)
        activity.topics_json = topics_json
        # Farbe wird automatisch basierend auf Typ zugewiesen (Light-Mode als Standard)
        activity.color = get_activity_color(activity_type, 'light')

        db.session.commit()
        recalculate_times(activity.training_id)
        flash('Aktivität erfolgreich aktualisiert!', 'success')
        return redirect(url_for('edit_training', id=activity.training_id))
    
    # GET: Formular anzeigen
    return render_template('activity_form.html', training=training, activity=activity, position_groups=POSITION_GROUPS, individual_mode_same=individual_mode_same, individual_common_topic=individual_common_topic, individual_topics=individual_topics)

@app.route('/activity/<int:id>/update', methods=['POST'])
@admin_required
def update_activity(id):
    activity = Activity.query.get_or_404(id)
    data = request.json

    activity.activity_type = data['activity_type']
    activity.duration = int(data['duration'])
    activity.position_groups = json.dumps(data['position_groups'])
    activity.topic = data.get('topic', '')
    activity.color = data.get('color', activity.color if hasattr(activity, 'color') else '#10b981')

    topics_json = None
    if data['activity_type'] == 'individual':
        topics_json = json.dumps(data.get('topics_per_group', {}))
    elif data['activity_type'] == 'group':
        topics_json = json.dumps(data.get('group_combinations', []))
    activity.topics_json = topics_json

    db.session.commit()
    recalculate_times(activity.training_id)

    return jsonify({'success': True})

@app.route('/activity/<int:id>/delete', methods=['POST'])
@admin_required
def delete_activity(id):
    activity = Activity.query.get_or_404(id)
    training_id = activity.training_id
    order_index = activity.order_index

    db.session.delete(activity)
    db.session.commit()

    recalculate_times(training_id)
    flash('Aktivität erfolgreich gelöscht!', 'success')
    
    if request.is_json:
        return jsonify({'success': True})
    return redirect(url_for('edit_training', id=training_id))

@app.route('/activity/<int:id>/move_up', methods=['POST'])
@admin_required
def move_activity_up(id):
    activity = Activity.query.get_or_404(id)
    training_id = activity.training_id
    
    prev_activity = Activity.query.filter_by(training_id=training_id, order_index=activity.order_index - 1).first()
    if prev_activity:
        activity.order_index, prev_activity.order_index = prev_activity.order_index, activity.order_index
        db.session.commit()
        recalculate_times(training_id)
        flash('Aktivität nach oben verschoben', 'success')
    
    return redirect(url_for('edit_training', id=training_id))

@app.route('/activity/<int:id>/move_down', methods=['POST'])
@admin_required
def move_activity_down(id):
    activity = Activity.query.get_or_404(id)
    training_id = activity.training_id
    
    next_activity = Activity.query.filter_by(training_id=training_id, order_index=activity.order_index + 1).first()
    if next_activity:
        activity.order_index, next_activity.order_index = next_activity.order_index, activity.order_index
        db.session.commit()
        recalculate_times(training_id)
        flash('Aktivität nach unten verschoben', 'success')
    
    return redirect(url_for('edit_training', id=training_id))

@app.route('/activity/reorder', methods=['POST'])
@admin_required
def reorder_activities():
    data = request.json
    training_id = data['training_id']
    activity_ids = data['activity_ids']

    for index, activity_id in enumerate(activity_ids):
        activity = Activity.query.get(activity_id)
        if activity:
            activity.order_index = index

    db.session.commit()
    recalculate_times(training_id)

    return jsonify({'success': True})

def recalculate_times(training_id):
    training = Training.query.get(training_id)
    activities = Activity.query.filter_by(training_id=training_id).order_by(Activity.order_index).all()

    if not activities:
        return

    first_activity = activities[0]
    if first_activity.activity_type == 'prepractice':
        start_datetime = datetime.combine(datetime.today(), training.start_time)
        start_datetime -= timedelta(minutes=first_activity.duration)
        first_activity.start_time = start_datetime.time()

        current_datetime = datetime.combine(datetime.today(), first_activity.start_time)
        current_datetime += timedelta(minutes=first_activity.duration)

        for activity in activities[1:]:
            activity.start_time = current_datetime.time()
            current_datetime += timedelta(minutes=activity.duration)
    else:
        current_time = training.start_time
        for activity in activities:
            activity.start_time = current_time
            current_datetime = datetime.combine(datetime.today(), current_time)
            current_datetime += timedelta(minutes=activity.duration)
            current_time = current_datetime.time()

    db.session.commit()

@app.route('/training/<int:id>/schedule')
def training_schedule(id):
    training = Training.query.get_or_404(id)
    dates = []
    current = training.start_date
    while current <= training.end_date:
        if current.weekday() == training.weekday:
            dates.append(current)
        current += timedelta(days=1)
    return render_template('schedule.html', training=training, dates=dates, position_groups=POSITION_GROUPS)

@app.template_filter('parse_groups')
def parse_groups(groups_json):
    try:
        return json.loads(groups_json)
    except:
        return []

@app.template_filter('from_json')
def from_json(json_string):
    try:
        return json.loads(json_string)
    except:
        return {}

@app.template_filter('get_activity_color')
def get_activity_color_filter(activity_type):
    """Template-Filter für Aktivitätsfarbe."""
    return get_activity_color(activity_type)

def get_text_color_for_bg(bg_color):
    """Berechnet die passende Textfarbe (schwarz/weiß) basierend auf der Hintergrundfarbe."""
    if not bg_color or not bg_color.startswith('#'):
        return 'black'
    try:
        rgb = bg_color[1:]
        r = int(rgb[0:2], 16)
        g = int(rgb[2:4], 16)
        b = int(rgb[4:6], 16)
        brightness = (r * 299 + g * 587 + b * 114) / 1000
        return 'white' if brightness < 128 else 'black'
    except:
        return 'black'

@app.template_filter('build_group_cells')
def build_group_cells(activity):
    # Reihenfolge muss mit der Tabelle übereinstimmen: OL, DL, LB, RB, DB, WR, TE, QB
    all_groups = ['OL', 'DL', 'LB', 'RB', 'DB', 'WR', 'TE', 'QB']
    cells = []
    # Verwende automatische Farbe basierend auf Typ (Light-Mode als Standard für Server-seitige Berechnung)
    activity_color = activity.color if hasattr(activity, 'color') and activity.color else get_activity_color(activity.activity_type, 'light')
    text_color = get_text_color_for_bg(activity_color)

    if activity.activity_type in ['team', 'prepractice']:
        position_groups_list = json.loads(activity.position_groups) if activity.position_groups else all_groups
        cells.append({
            'colspan': 8,  # 8 Gruppen-Spalten: OL, DL, LB, RB, DB, WR, TE, QB
            'class': 'table-success text-center',
            'content': activity.topic or '',
            'color': activity_color,
            'text_color': text_color,
            'groups': position_groups_list
        })
    elif activity.activity_type == 'individual':
        topics = json.loads(activity.topics_json) if activity.topics_json else {}
        for group in all_groups:
            # Erstelle separate Zellen für WR und TE, da die Tabelle separate Spalten hat
            if group == 'WR':
                cells.append({
                    'colspan': 1,
                    'groups': ['WR'],
                    'class': 'table-success',
                    'content': topics.get('WR', topics.get('TE', '')),
                    'color': activity_color,
                    'text_color': text_color
                })
            elif group == 'TE':
                # Erstelle auch eine TE-Zelle, da die Tabelle eine separate TE-Spalte hat
                cells.append({
                    'colspan': 1,
                    'groups': ['TE'],
                    'class': 'table-success',
                    'content': topics.get('TE', topics.get('WR', '')),
                    'color': activity_color,
                    'text_color': text_color
                })
            else:
                cells.append({
                    'colspan': 1,
                    'groups': [group],
                    'class': 'table-success',
                    'content': topics.get(group, ''),
                    'color': activity_color,
                    'text_color': text_color
                })
    elif activity.activity_type == 'group':
        combinations = json.loads(activity.topics_json) if activity.topics_json else []
        group_to_combo = {}
        for combo in combinations:
            for g in combo['groups']:
                group_to_combo[g] = combo

        rendered = set()
        for group in all_groups:
            # Überspringe TE in der Hauptschleife, wird bei WR behandelt
            if group == 'TE':
                continue

            # Spezialbehandlung für WR/TE
            # WR wurde möglicherweise bereits bei einer anderen Gruppe gerendert
            # Aber wir müssen die WR-Logik trotzdem ausführen, um TE zu behandeln
            if group == 'WR':
                # Prüfe, ob WR bereits gerendert wurde
                if group in rendered:
                    # WR wurde bereits gerendert, aber TE muss noch behandelt werden
                    if 'TE' not in rendered:
                        te_combo = group_to_combo.get('TE')
                        if te_combo:
                            cells.append({
                                'colspan': 1,
                                'groups': ['TE'],
                                'class': 'table-success',
                                'content': te_combo['topic'],
                                'color': activity_color,
                                'text_color': text_color
                            })
                        else:
                            cells.append({
                                'colspan': 1,
                                'groups': ['TE'],
                                'class': '',
                                'content': ' ',
                                'color': None,
                                'text_color': None
                            })
                        rendered.add('TE')
                    continue

                # WR wurde noch nicht gerendert
                wr_combo = group_to_combo.get('WR')
                te_combo = group_to_combo.get('TE')
                
                # Prüfe, ob WR und TE die gleiche Kombination haben
                if wr_combo and te_combo and wr_combo == te_combo:
                    # Prüfe, ob es mehr als nur WR und TE in der Kombination gibt
                    combo_groups = wr_combo['groups']
                    other_groups = [g for g in combo_groups if g not in ['WR', 'TE']]
                    
                    if other_groups:
                        # Es gibt andere Gruppen in der Kombination
                        # Erstelle separate Zellen für WR und TE
                        cells.append({
                            'colspan': 1,
                            'groups': ['WR'],
                            'class': 'table-success',
                            'content': wr_combo['topic'],
                            'color': activity_color,
                            'text_color': text_color
                        })
                        cells.append({
                            'colspan': 1,
                            'groups': ['TE'],
                            'class': 'table-success',
                            'content': te_combo['topic'],
                            'color': activity_color,
                            'text_color': text_color
                        })
                    else:
                        # Nur WR und TE in der Kombination - verbinde sie mit colspan=2
                        cells.append({
                            'colspan': 2,
                            'groups': ['WR', 'TE'],
                            'class': 'table-success',
                            'content': wr_combo['topic'],
                            'color': activity_color,
                            'text_color': text_color
                        })
                    rendered.add('WR')
                    rendered.add('TE')
                elif wr_combo and not te_combo:
                    # Nur WR hat eine Kombination
                    cells.append({
                        'colspan': 1,
                        'groups': ['WR'],
                        'class': 'table-success',
                        'content': wr_combo['topic'],
                        'color': activity_color,
                        'text_color': text_color
                    })
                    cells.append({
                        'colspan': 1,
                        'groups': ['TE'],
                        'class': '',
                        'content': ' ',
                        'color': None,
                        'text_color': None
                    })
                    rendered.add('WR')
                    rendered.add('TE')
                elif te_combo and not wr_combo:
                    # Nur TE hat eine Kombination
                    cells.append({
                        'colspan': 1,
                        'groups': ['WR'],
                        'class': '',
                        'content': ' ',
                        'color': None,
                        'text_color': None
                    })
                    cells.append({
                        'colspan': 1,
                        'groups': ['TE'],
                        'class': 'table-success',
                        'content': te_combo['topic'],
                        'color': activity_color,
                        'text_color': text_color
                    })
                    rendered.add('WR')
                    rendered.add('TE')
                else:
                    # Keine Kombination für WR oder TE
                    cells.append({
                        'colspan': 1,
                        'groups': ['WR'],
                        'class': '',
                        'content': ' ',
                        'color': None,
                        'text_color': None
                    })
                    cells.append({
                        'colspan': 1,
                        'groups': ['TE'],
                        'class': '',
                        'content': ' ',
                        'color': None,
                        'text_color': None
                    })
                    rendered.add('WR')
                    rendered.add('TE')
                continue
            
            # Normale Gruppen (nicht WR/TE)
            if group in rendered:
                continue

            combo = group_to_combo.get(group)
            if combo:
                combo_groups = combo['groups']
                consecutive_groups = [group]
                rendered.add(group)

                # Finde alle Gruppen in der Kombination, die in all_groups direkt aufeinander folgen
                # (ohne gruppenfremde Spalten dazwischen)
                next_idx = all_groups.index(group) + 1
                while next_idx < len(all_groups):
                    next_group = all_groups[next_idx]
                    
                    # Überspringe TE, wird bei WR behandelt
                    if next_group == 'TE':
                        next_idx += 1
                        continue
                    
                    # Wenn die nächste Gruppe bereits gerendert wurde, stoppe
                    if next_group in rendered:
                        break
                    
                    # Prüfe, ob die nächste Gruppe zur gleichen Kombination gehört
                    next_combo = group_to_combo.get(next_group)
                    
                    if next_group == 'WR' and next_combo == combo:
                        # WR gehört zur gleichen Kombination
                        consecutive_groups.append(next_group)
                        rendered.add(next_group)
                        # Prüfe auch TE: Nur hinzufügen, wenn TE die GLEICHE Kombination hat
                        te_combo = group_to_combo.get('TE')
                        if te_combo and te_combo == combo and 'TE' not in rendered:
                            consecutive_groups.append('TE')
                            rendered.add('TE')
                        next_idx += 1
                        continue
                    elif next_combo == combo:
                        # Die nächste Gruppe gehört zur gleichen Kombination
                        consecutive_groups.append(next_group)
                        rendered.add(next_group)
                        next_idx += 1
                    else:
                        # Die nächste Gruppe gehört zu einer anderen Kombination oder hat keine
                        # -> gruppenfremde Spalte, stoppe
                        break

                # Erstelle eine Zelle mit colspan für zusammenhängende Gruppen (verbindet sie visuell)
                cells.append({
                    'colspan': len(consecutive_groups),
                    'groups': consecutive_groups,
                    'class': 'table-success',
                    'content': combo['topic'],
                    'color': activity_color,
                    'text_color': text_color
                })
            else:
                # Erstelle eine leere Zelle für Gruppen ohne Kombination
                cells.append({
                    'colspan': 1,
                    'groups': [group],
                    'class': '',
                    'content': ' ',  # Leerzeichen statt leerem String, damit die Zelle gerendert wird
                    'color': None,
                    'text_color': None
                })
                rendered.add(group)

    return cells

if __name__ == '__main__':
    with app.app_context():
        # Führe Migrationen aus
        try:
            from migrate_add_color import migrate_add_color
            migrate_add_color()
        except ImportError:
            pass
        except Exception as e:
            app.logger.warning(f'Migration konnte nicht ausgeführt werden: {str(e)}')
        
        db.create_all()
        if User.query.count() == 0:
            admin = User(username='admin', role='admin')
            admin.set_password('admin')
            user = User(username='user', role='user')
            user.set_password('user')
            db.session.add(admin)
            db.session.add(user)
            db.session.commit()
            print('Default users created: admin/admin and user/user')
    app.run(debug=True)
