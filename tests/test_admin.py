from datetime import date, time

from app.extensions import db
from app.models import Training, TrainingInstance, ActivityInstance


def test_copy_training_instance_picks_next_free_date(client, app, login_as, csrf_token):
    login_response = login_as(username='admin', password='adminpw', role='admin')
    assert login_response.status_code == 302

    with app.app_context():
        training = Training(
            name='Admin Test',
            weekday=0,
            start_date=date(2025, 1, 1),
            end_date=date(2026, 12, 31),
            start_time=time(19, 0),
            is_hidden=False
        )
        db.session.add(training)
        db.session.flush()

        original = TrainingInstance(
            training_id=training.id,
            date=date(2025, 1, 6),
            status='active',
            start_time=time(19, 0)
        )
        blocker = TrainingInstance(
            training_id=training.id,
            date=date(2025, 1, 13),
            status='active',
            start_time=time(19, 0)
        )
        db.session.add(original)
        db.session.add(blocker)
        db.session.flush()

        db.session.add(ActivityInstance(
            training_instance_id=original.id,
            activity_type='team',
            start_time=time(19, 0),
            duration=45,
            position_groups='["OL","DL"]',
            topic='Install',
            order_index=0,
            topics_json=None,
            color='#10b981'
        ))
        db.session.commit()
        original_id = original.id
        training_id = training.id

    token = csrf_token('/admin/trainings')
    response = client.post(f'/training-instance/{original_id}/copy', data={'csrf_token': token})
    assert response.status_code == 302

    with app.app_context():
        instances = TrainingInstance.query.filter_by(training_id=training_id).order_by(TrainingInstance.date.asc()).all()
        assert len(instances) == 3
        copied = instances[-1]
        assert copied.date == date(2025, 1, 20)
        copied_activities = ActivityInstance.query.filter_by(training_instance_id=copied.id).all()
        assert len(copied_activities) == 1
        assert copied_activities[0].topic == 'Install'


def test_copy_training_instance_requires_admin(client, app, csrf_token):
    with app.app_context():
        training = Training(
            name='No Admin',
            weekday=2,
            start_date=date(2025, 1, 1),
            end_date=date(2026, 12, 31),
            start_time=time(18, 30),
            is_hidden=False
        )
        db.session.add(training)
        db.session.flush()
        instance = TrainingInstance(
            training_id=training.id,
            date=date(2025, 1, 8),
            status='active',
            start_time=time(18, 30)
        )
        db.session.add(instance)
        db.session.commit()
        instance_id = instance.id

    token = csrf_token('/login')
    response = client.post(f'/training-instance/{instance_id}/copy', data={'csrf_token': token})
    assert response.status_code == 302
    assert '/login' in response.location


def test_admin_trainings_hides_ended_by_default(client, app, login_as):
    login_response = login_as(username='admin2', password='adminpw', role='admin')
    assert login_response.status_code == 302

    with app.app_context():
        active = Training(
            name='ACTIVE TRAINING',
            weekday=2,
            start_date=date(2025, 1, 1),
            end_date=date(2099, 12, 31),
            start_time=time(19, 0),
            is_hidden=False
        )
        ended = Training(
            name='ENDED TRAINING',
            weekday=2,
            start_date=date(2024, 1, 1),
            end_date=date(2024, 12, 31),
            start_time=time(19, 0),
            is_hidden=False
        )
        db.session.add(active)
        db.session.add(ended)
        db.session.commit()

    response = client.get('/admin/trainings')
    assert response.status_code == 200
    body = response.get_data(as_text=True)
    assert 'ACTIVE TRAINING' in body
    assert 'ENDED TRAINING' not in body


def test_admin_trainings_can_show_ended(client, app, login_as):
    login_response = login_as(username='admin3', password='adminpw', role='admin')
    assert login_response.status_code == 302

    with app.app_context():
        ended = Training(
            name='ENDED VISIBLE TRAINING',
            weekday=4,
            start_date=date(2024, 1, 1),
            end_date=date(2024, 12, 31),
            start_time=time(18, 0),
            is_hidden=False
        )
        db.session.add(ended)
        db.session.commit()

    response = client.get('/admin/trainings?include_ended=1')
    assert response.status_code == 200
    body = response.get_data(as_text=True)
    assert 'ENDED VISIBLE TRAINING' in body
