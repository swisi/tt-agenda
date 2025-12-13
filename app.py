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

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Bitte melden Sie sich an.', 'warning')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Bitte melden Sie sich an.', 'warning')
            return redirect(url_for('login'))
        if session.get('user_role') != 'admin':
            flash('Sie haben keine Berechtigung für diese Aktion.', 'danger')
            return redirect(url_for('index'))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/')
@login_required
def index():
    trainings = Training.query.all()
    return render_template('index.html', trainings=trainings, weekdays=WEEKDAYS)

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
            return redirect(url_for('index'))
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
        'topics_json': a.topics_json
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

@app.route('/activity/add', methods=['POST'])
@admin_required
def add_activity():
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
        topics_json=topics_json
    )
    db.session.add(activity)
    db.session.commit()

    recalculate_times(data['training_id'])

    return jsonify({'id': activity.id, 'success': True})

@app.route('/activity/<int:id>/update', methods=['POST'])
@admin_required
def update_activity(id):
    activity = Activity.query.get_or_404(id)
    data = request.json

    activity.activity_type = data['activity_type']
    activity.duration = int(data['duration'])
    activity.position_groups = json.dumps(data['position_groups'])
    activity.topic = data.get('topic', '')

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

    return jsonify({'success': True})

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

@app.template_filter('build_group_cells')
def build_group_cells(activity):
    all_groups = ['OL', 'DL', 'LB', 'RB', 'DB', 'WR', 'TE', 'QB']
    cells = []

    if activity.activity_type in ['team', 'prepractice']:
        cells.append({
            'colspan': 7,
            'class': 'table-success text-center',
            'content': activity.topic or ''
        })
    elif activity.activity_type == 'individual':
        topics = json.loads(activity.topics_json) if activity.topics_json else {}
        for group in all_groups:
            if group == 'WR':
                cells.append({
                    'colspan': 1,
                    'class': 'table-success',
                    'content': topics.get('WR', topics.get('TE', ''))
                })
            elif group == 'TE':
                continue
            else:
                cells.append({
                    'colspan': 1,
                    'class': 'table-success',
                    'content': topics.get(group, '')
                })
    elif activity.activity_type == 'group':
        combinations = json.loads(activity.topics_json) if activity.topics_json else []
        group_to_combo = {}
        for combo in combinations:
            for g in combo['groups']:
                group_to_combo[g] = combo

        rendered = set()
        for group in all_groups:
            if group in rendered:
                continue

            if group == 'TE':
                continue

            if group == 'WR':
                wr_combo = group_to_combo.get('WR')
                te_combo = group_to_combo.get('TE')
                if wr_combo and te_combo and wr_combo == te_combo:
                    cells.append({
                        'colspan': 1,
                        'class': 'table-success' if wr_combo else '',
                        'content': wr_combo['topic'] if wr_combo else ''
                    })
                    rendered.add('WR')
                    rendered.add('TE')
                elif wr_combo or te_combo:
                    combo = wr_combo or te_combo
                    cells.append({
                        'colspan': 1,
                        'class': 'table-success' if combo else '',
                        'content': combo['topic'] if combo else ''
                    })
                    rendered.add('WR')
                    rendered.add('TE')
                else:
                    cells.append({
                        'colspan': 1,
                        'class': '',
                        'content': ''
                    })
                    rendered.add('WR')
                    rendered.add('TE')
                continue

            combo = group_to_combo.get(group)
            if combo:
                combo_groups = combo['groups']
                consecutive_groups = [group]
                rendered.add(group)

                next_idx = all_groups.index(group) + 1
                while next_idx < len(all_groups):
                    next_group = all_groups[next_idx]
                    if next_group == 'TE':
                        next_idx += 1
                        continue
                    if next_group in combo_groups and next_group not in rendered:
                        consecutive_groups.append(next_group)
                        rendered.add(next_group)
                        next_idx += 1
                    else:
                        break

                cells.append({
                    'colspan': len(consecutive_groups),
                    'class': 'table-success',
                    'content': combo['topic']
                })
            else:
                cells.append({
                    'colspan': 1,
                    'class': '',
                    'content': ''
                })
                rendered.add(group)

    return cells

if __name__ == '__main__':
    with app.app_context():
        if User.query.count() == 0:
            admin = User(username='admin', role='admin')
            admin.set_password('admin')
            user = User(username='user', role='user')
            user.set_password('user')
            db.session.add(admin)
            db.session.add(user)
            db.session.commit()
            print('Default users created: admin/admin and user/user')
        db.create_all()
    app.run(debug=True)
