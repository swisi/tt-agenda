from flask import Flask, render_template, request, redirect, url_for, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timedelta
import json

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///trainings.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class Training(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    weekday = db.Column(db.Integer, nullable=False)
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=False)
    start_time = db.Column(db.Time, nullable=False)
    prepractice_duration = db.Column(db.Integer, default=0)
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

WEEKDAYS = ['Montag', 'Dienstag', 'Mittwoch', 'Donnerstag', 'Freitag', 'Samstag', 'Sonntag']
POSITION_GROUPS = ['OL', 'DL', 'LB', 'DB', 'RB', 'QB', 'WR', 'TE']

@app.route('/')
def index():
    trainings = Training.query.all()
    return render_template('index.html', trainings=trainings, weekdays=WEEKDAYS)

@app.route('/training/new', methods=['GET', 'POST'])
def new_training():
    if request.method == 'POST':
        training = Training(
            name=request.form['name'],
            weekday=int(request.form['weekday']),
            start_date=datetime.strptime(request.form['start_date'], '%Y-%m-%d').date(),
            end_date=datetime.strptime(request.form['end_date'], '%Y-%m-%d').date(),
            start_time=datetime.strptime(request.form['start_time'], '%H:%M').time(),
            prepractice_duration=int(request.form.get('prepractice_duration', 0))
        )
        db.session.add(training)
        db.session.commit()
        return redirect(url_for('edit_training', id=training.id))
    return render_template('training_form.html', weekdays=WEEKDAYS)

@app.route('/training/<int:id>/edit', methods=['GET', 'POST'])
def edit_training(id):
    training = Training.query.get_or_404(id)
    if request.method == 'POST':
        training.name = request.form['name']
        training.weekday = int(request.form['weekday'])
        training.start_date = datetime.strptime(request.form['start_date'], '%Y-%m-%d').date()
        training.end_date = datetime.strptime(request.form['end_date'], '%Y-%m-%d').date()
        training.start_time = datetime.strptime(request.form['start_time'], '%H:%M').time()
        training.prepractice_duration = int(request.form.get('prepractice_duration', 0))
        db.session.commit()
        return redirect(url_for('edit_training', id=id))
    activities = Activity.query.filter_by(training_id=id).order_by(Activity.order_index).all()
    return render_template('training_edit.html', training=training, activities=activities, weekdays=WEEKDAYS, position_groups=POSITION_GROUPS)

@app.route('/training/<int:id>/delete', methods=['POST'])
def delete_training(id):
    training = Training.query.get_or_404(id)
    db.session.delete(training)
    db.session.commit()
    return redirect(url_for('index'))

@app.route('/activity/add', methods=['POST'])
def add_activity():
    data = request.json
    training = Training.query.get_or_404(data['training_id'])

    max_order = db.session.query(db.func.max(Activity.order_index)).filter_by(training_id=data['training_id']).scalar() or -1

    if max_order == -1:
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
    return jsonify({'id': activity.id, 'success': True})

@app.route('/activity/<int:id>/delete', methods=['POST'])
def delete_activity(id):
    activity = Activity.query.get_or_404(id)
    training_id = activity.training_id
    order_index = activity.order_index

    db.session.delete(activity)
    db.session.commit()

    recalculate_times(training_id)

    return jsonify({'success': True})

@app.route('/activity/reorder', methods=['POST'])
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

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
