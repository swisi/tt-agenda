def _sample_activities():
    return [
        {
            "activity_type": "individual",
            "duration_minutes": 60,
            "topic": "Technique",
            "position_codes": ["OL", "DL"],
            "position_groups": ["Line"],
        },
        {
            "activity_type": "team",
            "duration_minutes": 60,
            "topic": "Team",
            "position_codes": [],
            "position_groups": [],
        },
    ]


def test_template_schedule_with_computed_end_time(client):
    create_group = client.post(
        "/api/v1/position-groups",
        json={"name": "Line", "position_codes": ["OL", "DL"]},
    )
    assert create_group.status_code == 201

    create_template = client.post(
        "/api/v1/templates",
        json={
            "name": "Mittwoch Training",
            "valid_from": "2026-03-01",
            "valid_to": "2026-03-31",
            "weekday": 2,
            "start_time": "19:30",
            "activities": _sample_activities(),
        },
    )
    assert create_template.status_code == 201

    response = client.get("/api/v1/schedule?from=2026-03-01&to=2026-03-31")
    assert response.status_code == 200
    payload = response.json()

    assert payload["count"] == 4
    for item in payload["items"]:
        assert item["source"] == "template"
        assert item["start_time"] == "19:30"
        assert item["end_time"] == "21:30"


def test_override_keeps_specific_day_and_template_changes_future(client):
    create_template = client.post(
        "/api/v1/templates",
        json={
            "name": "Mittwoch Training",
            "valid_from": "2026-03-01",
            "valid_to": "2026-03-31",
            "weekday": 2,
            "start_time": "19:30",
            "activities": _sample_activities(),
        },
    )
    template_id = create_template.json()["id"]

    override = client.post(
        f"/api/v1/templates/{template_id}/overrides",
        json={
            "date": "2026-03-11",
            "start_time": "20:00",
            "activities": [
                {
                    "activity_type": "individual",
                    "duration_minutes": 30,
                    "topic": "Short Unit",
                    "position_codes": ["LB"],
                    "position_groups": [],
                }
            ],
        },
    )
    assert override.status_code == 201

    patch_template = client.patch(f"/api/v1/templates/{template_id}", json={"start_time": "18:00"})
    assert patch_template.status_code == 200

    response = client.get("/api/v1/schedule?from=2026-03-01&to=2026-03-31")
    items = response.json()["items"]

    by_date = {item["date"]: item for item in items}
    assert by_date["2026-03-11"]["start_time"] == "20:00"
    assert by_date["2026-03-11"]["end_time"] == "20:30"
    assert by_date["2026-03-11"]["is_override"] is True

    assert by_date["2026-03-18"]["start_time"] == "18:00"
    assert by_date["2026-03-25"]["start_time"] == "18:00"


def test_adhoc_instance_is_in_schedule(client):
    create_adhoc = client.post(
        "/api/v1/instances/adhoc",
        json={
            "name": "Zusatztraining",
            "date": "2026-03-14",
            "start_time": "10:00",
            "activities": [
                {
                    "activity_type": "group",
                    "duration_minutes": 90,
                    "topic": "Special",
                    "position_codes": ["WR", "RB"],
                    "position_groups": [],
                }
            ],
        },
    )
    assert create_adhoc.status_code == 201

    response = client.get("/api/v1/schedule?from=2026-03-01&to=2026-03-31")
    assert response.status_code == 200
    items = response.json()["items"]

    adhoc = [item for item in items if item["source"] == "ad_hoc"]
    assert len(adhoc) == 1
    assert adhoc[0]["date"] == "2026-03-14"
    assert adhoc[0]["end_time"] == "11:30"
