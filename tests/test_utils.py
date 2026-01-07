import pytest
from datetime import datetime, timedelta
from app.utils import build_activity_timeline, get_text_color_for_bg, build_group_cells
from app.models import Activity

def test_build_activity_timeline():
    # Mock activities
    class MockActivity:
        def __init__(self, start_time, duration):
            self.start_time = start_time
            self.duration = duration

    activities = [
        MockActivity(datetime(2023, 1, 1, 10, 0).time(), 60),
        MockActivity(datetime(2023, 1, 1, 11, 0).time(), 30),
    ]
    base_date = datetime(2023, 1, 1).date()
    timeline = build_activity_timeline(activities, base_date)
    assert len(timeline) == 2
    assert timeline[0][1] == datetime(2023, 1, 1, 10, 0)
    assert timeline[1][1] == datetime(2023, 1, 1, 11, 0)

def test_get_text_color_for_bg():
    assert get_text_color_for_bg('#000000') == 'white'
    assert get_text_color_for_bg('#FFFFFF') == 'black'
    assert get_text_color_for_bg('#808080') == 'black'  # Borderline, but returns black

def test_build_group_cells_team():
    # Mock activity for team
    class MockActivity:
        def __init__(self, activity_type, position_groups, topic, color=None):
            self.activity_type = activity_type
            self.position_groups = position_groups
            self.topic = topic
            self.color = color

    activity = MockActivity('team', '["OL", "DL"]', 'Team Topic')
    cells = build_group_cells(activity)
    assert len(cells) == 1
    assert cells[0]['colspan'] == 8
    assert cells[0]['content'] == 'Team Topic'