from datetime import datetime, timedelta
from flask import session, flash, redirect, url_for, request
from functools import wraps
import json
from typing import List, Tuple, Optional, Dict, Any
from .models import Activity, Training
from .extensions import db

WEEKDAYS = ['Montag', 'Dienstag', 'Mittwoch', 'Donnerstag', 'Freitag', 'Samstag', 'Sonntag']
POSITION_GROUPS = ['OL', 'DL', 'LB', 'RB','DB', 'TE', 'WR', 'QB']

try:
    from .activity_colors import get_activity_color, LIGHT_MODE_COLORS, DARK_MODE_COLORS
except ImportError:
    # Fallback colors if activity_colors.py is missing
    LIGHT_MODE_COLORS = {'team': '#A8D5E2', 'prepractice': '#FFD6CC', 'individual': '#D4E4C5', 'group': '#FFE5B4'}
    DARK_MODE_COLORS = {'team': '#4A90A4', 'prepractice': '#C97A6B', 'individual': '#7A9B6B', 'group': '#C9A86B'}

    def get_activity_color(activity_type, theme='light'):
        color_map = DARK_MODE_COLORS if theme == 'dark' else LIGHT_MODE_COLORS
        return color_map.get(activity_type, '#E8E8E8' if theme == 'light' else '#4A4A4A')

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Bitte melden Sie sich an.', 'warning')
            return redirect(url_for('auth.login', next=request.url))
        return f(*args, **kwargs)
    return decorated_function

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Bitte melden Sie sich an.', 'warning')
            return redirect(url_for('auth.login', next=request.url))
        if session.get('user_role') != 'admin':
            flash('Sie haben keine Berechtigung für diese Aktion.', 'danger')
            return redirect(url_for('main.index'))
        return f(*args, **kwargs)
    return decorated_function

def build_activity_timeline(activities: List[Activity], base_date: datetime.date) -> List[Tuple[Activity, datetime, datetime]]:
    """Erstellt eine Timeline mit Datetimes, inkl. Mitternachts-Überlauf."""
    timeline = []
    current_date = base_date
    last_start = None

    for activity in activities:
        activity_start = datetime.combine(current_date, activity.start_time)
        if last_start and activity_start <= last_start:
            current_date += timedelta(days=1)
            activity_start = datetime.combine(current_date, activity.start_time)

        activity_end = activity_start + timedelta(minutes=activity.duration)
        timeline.append((activity, activity_start, activity_end))
        last_start = activity_start

    return timeline

def get_training_timeline(training: Training, base_date: datetime.date) -> Tuple[Optional[List[Activity]], Optional[List[Tuple[Activity, datetime, datetime]]], Optional[datetime], Optional[datetime]]:
    """Lädt Aktivitäten und berechnet die Timeline für ein Datum."""
    activities = Activity.query.filter_by(training_id=training.id).order_by(Activity.order_index).all()
    if not activities:
        return None, None, None, None

    timeline = build_activity_timeline(activities, base_date)
    if not timeline:
        return activities, None, None, None

    return activities, timeline, timeline[0][1], timeline[-1][2]

def get_next_training_dates(training, limit=3):
    """Berechnet die nächsten Trainingstermine für ein Training."""
    now = datetime.now()
    today = now.date()
    dates = []

    if training.end_date < today:
        return dates

    start = max(today, training.start_date)
    days_ahead = (training.weekday - start.weekday()) % 7
    current = start + timedelta(days=days_ahead)
    target_limit = float('inf') if limit is None else limit

    while current <= training.end_date and len(dates) < target_limit:
        if current == today:
            activities = Activity.query.filter_by(training_id=training.id).order_by(Activity.order_index, Activity.id).all()
            if activities:
                timeline = build_activity_timeline(activities, today)
                if timeline and now < timeline[-1][2]:
                    dates.append(current)
        else:
            dates.append(current)
        current += timedelta(days=7)

    return dates

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

def build_group_cells(activity: Activity) -> List[Dict[str, Any]]:
    all_groups = ['OL', 'DL', 'LB', 'RB', 'DB', 'WR', 'TE', 'QB']
    group_tone_map = {
        'OL': 0,
        'DL': 1,
        'LB': 2,
        'RB': 3,
        'DB': 4,
        'WR': 5,
        'TE': 6,
        'QB': 7
    }
    cells = []
    activity_color = activity.color if hasattr(activity, 'color') and activity.color else get_activity_color(activity.activity_type, 'light')
    text_color = get_text_color_for_bg(activity_color)

    def with_tone_class(base_class: str, groups: List[str]) -> str:
        if not groups:
            return base_class
        tone = group_tone_map.get(groups[0])
        if tone is None:
            return base_class
        return f"{base_class} group-tone-{tone}".strip()

    if activity.activity_type in ['team', 'prepractice']:
        position_groups_list = json.loads(activity.position_groups) if activity.position_groups else all_groups
        cells.append({
            'colspan': 8,
            'class': 'table-success text-center',
            'content': activity.topic or '',
            'color': activity_color,
            'text_color': text_color,
            'groups': position_groups_list
        })
    elif activity.activity_type == 'individual':
        cells.extend(_build_individual_cells(activity, all_groups, activity_color, text_color, with_tone_class))
    elif activity.activity_type == 'group':
        cells.extend(_build_group_cells(activity, all_groups, activity_color, text_color, with_tone_class))

    return cells

def _build_individual_cells(activity: Activity, all_groups: List[str], activity_color: str, text_color: str, with_tone_class) -> List[Dict[str, Any]]:
    cells = []
    topics = json.loads(activity.topics_json) if activity.topics_json else {}
    for group in all_groups:
        if group == 'WR':
            cells.append({
                'colspan': 1,
                'groups': ['WR'],
                'class': with_tone_class('table-success', ['WR']),
                'content': topics.get('WR', topics.get('TE', '')),
                'color': activity_color,
                'text_color': text_color
            })
        elif group == 'TE':
            cells.append({
                'colspan': 1,
                'groups': ['TE'],
                'class': with_tone_class('table-success', ['TE']),
                'content': topics.get('TE', topics.get('WR', '')),
                'color': activity_color,
                'text_color': text_color
            })
        else:
            cells.append({
                'colspan': 1,
                'groups': [group],
                'class': with_tone_class('table-success', [group]),
                'content': topics.get(group, ''),
                'color': activity_color,
                'text_color': text_color
            })
    return cells

def _build_group_cells(activity: Activity, all_groups: List[str], activity_color: str, text_color: str, with_tone_class) -> List[Dict[str, Any]]:
    cells = []
    combinations = json.loads(activity.topics_json) if activity.topics_json else []
    group_to_combo = {g: combo for combo in combinations for g in combo['groups']}
    rendered = set()

    for group in all_groups:
        if group in rendered:
            continue

        combo = group_to_combo.get(group)
        if combo:
            consecutive_groups = _find_consecutive_groups(group, all_groups, group_to_combo, rendered)
            cells.append({
                'colspan': len(consecutive_groups),
                'groups': consecutive_groups,
                'class': with_tone_class('table-success', consecutive_groups),
                'content': combo['topic'],
                'color': activity_color,
                'text_color': text_color
            })
        else:
            cells.append({
                'colspan': 1,
                'groups': [group],
                'class': '',
                'content': ' ',
                'color': None,
                'text_color': None
            })
            rendered.add(group)

    return cells

def _find_consecutive_groups(start_group: str, all_groups: List[str], group_to_combo: Dict[str, Dict], rendered: set) -> List[str]:
    consecutive_groups = [start_group]
    rendered.add(start_group)
    combo = group_to_combo[start_group]

    idx = all_groups.index(start_group) + 1
    while idx < len(all_groups):
        next_group = all_groups[idx]
        if next_group in rendered or group_to_combo.get(next_group) != combo:
            break
        consecutive_groups.append(next_group)
        rendered.add(next_group)
        idx += 1

    return consecutive_groups

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
