from flask import Blueprint, render_template, request
from datetime import datetime, timedelta
from ..models import Training, Activity
from ..utils import login_required, get_next_training_dates, build_activity_timeline, get_training_timeline, WEEKDAYS, POSITION_GROUPS

bp = Blueprint('main', __name__)

@bp.route('/')
@login_required
def index():
    trainings = Training.query.all()
    
    now = datetime.now()
    today = now.date()
    yesterday = today - timedelta(days=1)
    today_weekday = today.weekday()
    
    current_training = None
    current_activity = None
    next_activity = None
    training_status = None
    upcoming_start = None
    
    upcoming_trainings = []
    
    for training in trainings:
        next_dates = get_next_training_dates(training, limit=3)
        for date in next_dates:
            activities = Activity.query.filter_by(training_id=training.id).order_by(Activity.order_index).all()
            if activities:
                timeline = build_activity_timeline(activities, date)
                if not timeline:
                    continue

                training_start_datetime = timeline[0][1]
                training_end_datetime = timeline[-1][2]
                
                is_today = date == today
                is_running = False
                is_upcoming = False
                
                if is_today:
                    if now >= training_start_datetime and now < training_end_datetime:
                        is_running = True
                    elif now < training_start_datetime:
                        is_upcoming = True
                
                upcoming_trainings.append({
                    'training': training,
                    'date': date,
                    'start_time': training_start_datetime.time(),
                    'end_time': training_end_datetime.time(),
                    'is_today': is_today,
                    'is_running': is_running,
                    'is_upcoming': is_upcoming
                })
    
    upcoming_trainings.sort(key=lambda x: (x['date'], x['start_time']))
    
    for training in trainings:
        for candidate_date in (yesterday, today):
            if training.weekday != candidate_date.weekday():
                continue
            if not (training.start_date <= candidate_date <= training.end_date):
                continue

            activities, timeline, start_dt, end_dt = get_training_timeline(training, candidate_date)
            if not timeline:
                continue

            if start_dt <= now < end_dt:
                current_training = training
                training_status = 'running'

                for i, (activity, activity_start, activity_end) in enumerate(timeline):
                    if activity_start <= now < activity_end:
                        current_activity = activity
                        if i + 1 < len(timeline):
                            next_activity = timeline[i + 1][0]
                        break
                    elif now < activity_start:
                        next_activity = activity
                        break
                break
        if training_status == 'running':
            break

        if training.weekday == today_weekday and training.start_date <= today <= training.end_date:
            activities, timeline, start_dt, end_dt = get_training_timeline(training, today)
            if timeline and now < start_dt:
                if upcoming_start is None or start_dt < upcoming_start:
                    current_training = training
                    training_status = 'upcoming'
                    next_activity = timeline[0][0]
                    current_activity = None
                    upcoming_start = start_dt
    
    return render_template('index.html', 
                         trainings=trainings, 
                         weekdays=WEEKDAYS,
                         position_groups=POSITION_GROUPS,
                         upcoming_trainings=upcoming_trainings[:3],
                         current_training=current_training,
                         current_activity=current_activity,
                         next_activity=next_activity,
                         training_status=training_status,
                         now=now)

@bp.route('/live')
@login_required
def live():
    trainings = Training.query.all()
    
    now = datetime.now()
    today = now.date()
    yesterday = today - timedelta(days=1)
    today_weekday = today.weekday()
    
    current_training = None
    current_activity = None
    next_activity = None
    training_status = None
    upcoming_start = None

    selected_training_id = request.args.get('training_id', type=int)
    selected_date_str = request.args.get('date')
    selected_date = None
    if selected_training_id and selected_date_str:
        try:
            selected_date = datetime.strptime(selected_date_str, '%Y-%m-%d').date()
        except ValueError:
            selected_date = None

    if selected_training_id and selected_date:
        training = Training.query.get_or_404(selected_training_id)
        if training.start_date <= selected_date <= training.end_date and training.weekday == selected_date.weekday():
            activities, timeline, start_dt, end_dt = get_training_timeline(training, selected_date)
        else:
            activities, timeline, start_dt, end_dt = None, None, None, None

        if timeline:
            current_training = training
            if selected_date == today:
                if start_dt <= now < end_dt:
                    training_status = 'running'
                    for i, (activity, activity_start, activity_end) in enumerate(timeline):
                        if activity_start <= now < activity_end:
                            current_activity = activity
                            if i + 1 < len(timeline):
                                next_activity = timeline[i + 1][0]
                            break
                        elif now < activity_start:
                            next_activity = activity
                            break
                elif now < start_dt:
                    training_status = 'upcoming'
                    next_activity = timeline[0][0]
        return render_template('live.html', 
                             weekdays=WEEKDAYS,
                             position_groups=POSITION_GROUPS,
                             current_training=current_training,
                             current_activity=current_activity,
                             next_activity=next_activity,
                             training_status=training_status,
                             now=now)
    
    for training in trainings:
        for candidate_date in (yesterday, today):
            if training.weekday != candidate_date.weekday():
                continue
            if not (training.start_date <= candidate_date <= training.end_date):
                continue

            activities, timeline, start_dt, end_dt = get_training_timeline(training, candidate_date)
            if not timeline:
                continue

            if start_dt <= now < end_dt:
                current_training = training
                training_status = 'running'

                for i, (activity, activity_start, activity_end) in enumerate(timeline):
                    if activity_start <= now < activity_end:
                        current_activity = activity
                        if i + 1 < len(timeline):
                            next_activity = timeline[i + 1][0]
                        break
                    elif now < activity_start:
                        next_activity = activity
                        break
                break
        if training_status == 'running':
            break

        if training.weekday == today_weekday and training.start_date <= today <= training.end_date:
            activities, timeline, start_dt, end_dt = get_training_timeline(training, today)
            if timeline and now < start_dt:
                if upcoming_start is None or start_dt < upcoming_start:
                    current_training = training
                    training_status = 'upcoming'
                    next_activity = timeline[0][0]
                    current_activity = None
                    upcoming_start = start_dt
    
    return render_template('live.html', 
                         weekdays=WEEKDAYS,
                         position_groups=POSITION_GROUPS,
                         current_training=current_training,
                         current_activity=current_activity,
                         next_activity=next_activity,
                         training_status=training_status,
                         now=now)

@bp.route('/test')
def test():
    return '<h1>Flask funktioniert!</h1><p>Gehe zu <a href="/login">/login</a></p>'
