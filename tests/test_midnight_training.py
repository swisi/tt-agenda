import json
import sys
import unittest
from contextlib import contextmanager
from datetime import datetime, date, time
from unittest.mock import patch
from pathlib import Path

from flask import template_rendered

ROOT_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT_DIR))

from app import app, db, Training, Activity


@contextmanager
def captured_templates(flask_app):
    recorded = []

    def receiver(sender, template, context, **extra):
        recorded.append((template, context))

    template_rendered.connect(receiver, flask_app)
    try:
        yield recorded
    finally:
        template_rendered.disconnect(receiver, flask_app)


class MidnightTrainingTest(unittest.TestCase):
    def setUp(self):
        app.config.update(
            TESTING=True,
            SQLALCHEMY_DATABASE_URI="sqlite:///:memory:",
        )
        self.app = app
        self.client = app.test_client()

        with self.app.app_context():
            db.drop_all()
            db.create_all()

            training = Training(
                name="Mittwoch spaet",
                weekday=2,  # Mittwoch
                start_date=date(2024, 1, 1),
                end_date=date(2024, 1, 31),
                start_time=time(21, 30),
            )
            db.session.add(training)
            db.session.flush()

            activities = [
                Activity(
                    training_id=training.id,
                    activity_type="team",
                    start_time=time(21, 30),
                    duration=60,
                    position_groups=json.dumps([]),
                    order_index=0,
                ),
                Activity(
                    training_id=training.id,
                    activity_type="team",
                    start_time=time(22, 30),
                    duration=60,
                    position_groups=json.dumps([]),
                    order_index=1,
                ),
                Activity(
                    training_id=training.id,
                    activity_type="team",
                    start_time=time(23, 30),
                    duration=35,
                    position_groups=json.dumps([]),
                    order_index=2,
                ),
            ]
            db.session.add_all(activities)
            db.session.commit()

        with self.client.session_transaction() as session:
            session["user_id"] = 1
            session["user_role"] = "admin"

    def tearDown(self):
        with self.app.app_context():
            db.drop_all()

    def test_live_shows_training_running_after_midnight(self):
        with captured_templates(self.app) as templates:
            with patch("app.datetime", wraps=datetime) as mock_datetime:
                mock_datetime.now.return_value = datetime(2024, 1, 4, 0, 2)
                response = self.client.get("/live")

        self.assertEqual(response.status_code, 200)
        self.assertTrue(templates)
        context = templates[0][1]
        self.assertEqual(context["training_status"], "running")
        self.assertIsNotNone(context["current_training"])

    def test_index_shows_training_running_after_midnight(self):
        with captured_templates(self.app) as templates:
            with patch("app.datetime", wraps=datetime) as mock_datetime:
                mock_datetime.now.return_value = datetime(2024, 1, 4, 0, 2)
                response = self.client.get("/")

        self.assertEqual(response.status_code, 200)
        self.assertTrue(templates)
        context = templates[0][1]
        self.assertEqual(context["training_status"], "running")
        self.assertIsNotNone(context["current_training"])
