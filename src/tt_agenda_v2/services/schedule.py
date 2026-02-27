from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import date, datetime, time, timedelta

from sqlalchemy import and_, select
from sqlalchemy.orm import Session, selectinload

from tt_agenda_v2.models import AdHocTrainingInstance, ActivityTemplate, PositionGroup, TrainingOverride, TrainingTemplate


@dataclass
class ScheduleItem:
    source: str
    name: str
    date: date
    start_time: time
    end_time: time
    activities: list[dict]
    is_override: bool = False

    def to_dict(self) -> dict:
        return {
            "source": self.source,
            "name": self.name,
            "date": self.date.isoformat(),
            "start_time": self.start_time.strftime("%H:%M"),
            "end_time": self.end_time.strftime("%H:%M"),
            "activities": self.activities,
            "is_override": self.is_override,
        }


def parse_time(value: str) -> time:
    return datetime.strptime(value, "%H:%M").time()


def _compute_end_time(start_time: time, activities: list[dict]) -> time:
    total_minutes = sum(max(0, int(activity.get("duration_minutes", 0))) for activity in activities)
    start_dt = datetime.combine(date(2000, 1, 1), start_time)
    return (start_dt + timedelta(minutes=total_minutes)).time()


def _serialize_activities(rows: list[ActivityTemplate], groups_by_name: dict[str, list[str]]) -> list[dict]:
    serialized: list[dict] = []
    for row in rows:
        groups = row.position_group_names
        group_positions: list[str] = []
        for group_name in groups:
            group_positions.extend(groups_by_name.get(group_name, []))

        effective_positions = sorted({*row.position_codes, *group_positions})
        serialized.append(
            {
                "activity_type": row.activity_type,
                "duration_minutes": row.duration_minutes,
                "topic": row.topic,
                "order_index": row.order_index,
                "position_codes": row.position_codes,
                "position_groups": groups,
                "effective_position_codes": effective_positions,
            }
        )
    return serialized


def _matching_dates(start_date: date, end_date: date, weekday: int) -> list[date]:
    current = start_date
    dates: list[date] = []
    while current <= end_date:
        if current.weekday() == weekday:
            dates.append(current)
        current += timedelta(days=1)
    return dates


def build_schedule(db: Session, from_date: date, to_date: date) -> list[dict]:
    groups = db.scalars(select(PositionGroup)).all()
    groups_by_name = {group.name: group.position_codes for group in groups}

    templates = db.scalars(
        select(TrainingTemplate)
        .where(
            and_(
                TrainingTemplate.is_active.is_(True),
                TrainingTemplate.valid_to >= from_date,
                TrainingTemplate.valid_from <= to_date,
            )
        )
        .options(selectinload(TrainingTemplate.activities))
    ).all()

    overrides = db.scalars(
        select(TrainingOverride).where(
            and_(
                TrainingOverride.date >= from_date,
                TrainingOverride.date <= to_date,
            )
        )
    ).all()
    overrides_by_key = {(override.training_template_id, override.date): override for override in overrides}

    result: list[ScheduleItem] = []

    for template in templates:
        range_start = max(from_date, template.valid_from)
        range_end = min(to_date, template.valid_to)
        template_activities = _serialize_activities(template.activities, groups_by_name)

        for day in _matching_dates(range_start, range_end, template.weekday):
            override = overrides_by_key.get((template.id, day))
            if override and override.cancelled:
                continue

            start_time = override.start_time if override and override.start_time else template.start_time
            activities = json.loads(override.activities_json) if override and override.activities_json else template_activities

            end_time = _compute_end_time(start_time, activities)
            result.append(
                ScheduleItem(
                    source="template",
                    name=template.name,
                    date=day,
                    start_time=start_time,
                    end_time=end_time,
                    activities=activities,
                    is_override=bool(override),
                )
            )

    adhoc_rows = db.scalars(
        select(AdHocTrainingInstance).where(
            and_(
                AdHocTrainingInstance.date >= from_date,
                AdHocTrainingInstance.date <= to_date,
            )
        )
    ).all()
    for row in adhoc_rows:
        activities = json.loads(row.activities_json or "[]")
        end_time = _compute_end_time(row.start_time, activities)
        result.append(
            ScheduleItem(
                source="ad_hoc",
                name=row.name,
                date=row.date,
                start_time=row.start_time,
                end_time=end_time,
                activities=activities,
                is_override=False,
            )
        )

    result.sort(key=lambda item: (item.date, item.start_time, item.name))
    return [item.to_dict() for item in result]
