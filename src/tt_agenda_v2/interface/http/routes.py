from __future__ import annotations

import json
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
import pathlib
from fastapi import WebSocket, WebSocketDisconnect
import asyncio
from hashlib import sha256
import json as _json
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, selectinload

from tt_agenda_v2.database import get_db
from tt_agenda_v2 import database
from tt_agenda_v2.models import AdHocTrainingInstance, ActivityTemplate, PositionGroup, TrainingOverride, TrainingTemplate, User
from tt_agenda_v2.services.schedule import build_schedule, parse_time

router = APIRouter()

# Setup templates directory relative to package
# file is .../interface/http/routes.py -> go up three levels to reach package root
_pkg_dir = pathlib.Path(__file__).resolve().parent.parent.parent
templates = Jinja2Templates(directory=str(_pkg_dir / "templates"))


def _parse_date(value: str):
    try:
        return datetime.strptime(value, "%Y-%m-%d").date()
    except ValueError as exc:
        raise HTTPException(status_code=400, detail="Ungültiges Datumsformat. Erwartet: YYYY-MM-DD") from exc


def _template_to_dict(template: TrainingTemplate) -> dict:
    return {
        "id": template.id,
        "name": template.name,
        "valid_from": template.valid_from.isoformat(),
        "valid_to": template.valid_to.isoformat(),
        "weekday": template.weekday,
        "start_time": template.start_time.strftime("%H:%M"),
        "is_active": template.is_active,
        "activities": [
            {
                "id": activity.id,
                "activity_type": activity.activity_type,
                "duration_minutes": activity.duration_minutes,
                "topic": activity.topic,
                "order_index": activity.order_index,
                "position_codes": activity.position_codes,
                "position_groups": activity.position_group_names,
            }
            for activity in template.activities
        ],
    }


def _require_template(db: Session, template_id: int) -> TrainingTemplate:
    template = db.get(TrainingTemplate, template_id)
    if template is None:
        raise HTTPException(status_code=404, detail="Template nicht gefunden.")
    return template


class ConnectionManager:
    def __init__(self):
        self.active: set[WebSocket] = set()

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active.add(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active.discard(websocket)

    async def send_json(self, websocket: WebSocket, message: object):
        await websocket.send_json(message)

    async def broadcast(self, message: object):
        to_remove = []
        for ws in list(self.active):
            try:
                await ws.send_json(message)
            except Exception:
                to_remove.append(ws)
        for ws in to_remove:
            self.active.discard(ws)


manager = ConnectionManager()


def _compute_today_schedule_serialized() -> str:
    """Return a canonical serialized representation of today's schedule."""
    if database.SessionLocal is None:
        return ""
    db = database.SessionLocal()
    try:
        today = datetime.utcnow().date()
        items = build_schedule(db, today, today)
        # sort and produce deterministic JSON
        s = _json.dumps(items, sort_keys=True, ensure_ascii=False)
        return sha256(s.encode('utf-8')).hexdigest(), s
    finally:
        db.close()


def _schedule_message_from_serialized(s: str) -> object:
    try:
        return {"ok": True, "items": _json.loads(s), "count": len(_json.loads(s))}
    except Exception:
        return {"ok": True, "items": [], "count": 0}


@router.get("/health/live")
def health_live():
    return {"status": "ok", "service": "tt-agenda-v2"}


@router.get("/health/ready")
def health_ready():
    return {"status": "ready"}


@router.get("/", include_in_schema=False)
def root_view(request: Request):
    # Render a simple server-side live view.
    return templates.TemplateResponse("live.html", {"request": request})


@router.get("/templates", include_in_schema=False)
def templates_page(request: Request, db: Session = Depends(get_db)):
    rows = db.scalars(select(TrainingTemplate).options(selectinload(TrainingTemplate.activities)).order_by(TrainingTemplate.name.asc())).all()
    return templates.TemplateResponse("templates_list.html", {"request": request, "templates": rows})


@router.get("/templates/{template_id}/edit", include_in_schema=False)
def template_edit(request: Request, template_id: int, db: Session = Depends(get_db)):
    tpl = db.get(TrainingTemplate, template_id)
    if tpl is None:
        raise HTTPException(status_code=404, detail="Template nicht gefunden")
    return templates.TemplateResponse("template_form.html", {"request": request, "template": tpl})


@router.post("/templates/{template_id}/edit", include_in_schema=False)
async def template_edit_post(request: Request, template_id: int, db: Session = Depends(get_db)):
    tpl = db.get(TrainingTemplate, template_id)
    if tpl is None:
        raise HTTPException(status_code=404, detail="Template nicht gefunden")

    # avoid requiring python-multipart in tests/environments: parse urlencoded body
    raw = await request.body()
    try:
        from urllib.parse import parse_qs

        parsed = parse_qs(raw.decode())
        form = {k: v[0] for k, v in parsed.items()}
    except Exception:
        form = {}

    def fv(key, default=None):
        val = form.get(key)
        if val is None:
            return default
        return str(val)

    if fv("name") is not None:
        tpl.name = fv("name").strip()
    if fv("weekday") is not None:
        try:
            tpl.weekday = int(fv("weekday"))
        except ValueError:
            pass
    if fv("start_time") is not None:
        try:
            tpl.start_time = parse_time(fv("start_time"))
        except Exception:
            pass

    tpl.is_active = True if form.get("is_active") in ("on", "true", "1") else False

    db.commit()
    return RedirectResponse(url="/templates", status_code=303)


@router.post("/auth/login")
def login(payload: dict, db: Session = Depends(get_db)):
    username = payload.get("username", "")
    password = payload.get("password", "")

    user = db.scalar(select(User).where(User.username == username))
    if user is None or not user.check_password(password):
        raise HTTPException(status_code=401, detail="Ungültiger Benutzername oder Passwort.")

    return {"ok": True, "username": user.username, "role": user.role}


@router.get("/api/v1/position-groups")
def list_position_groups(db: Session = Depends(get_db)):
    rows = db.scalars(select(PositionGroup).order_by(PositionGroup.name.asc())).all()
    return [
        {
            "id": row.id,
            "name": row.name,
            "position_codes": row.position_codes,
        }
        for row in rows
    ]


@router.post("/api/v1/position-groups", status_code=status.HTTP_201_CREATED)
def create_position_group(payload: dict, db: Session = Depends(get_db)):
    group = PositionGroup(name=payload["name"].strip())
    group.position_codes = payload.get("position_codes", [])
    db.add(group)
    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(status_code=409, detail="Positionsgruppe existiert bereits.") from exc
    db.refresh(group)
    try:
        if database.SessionLocal is not None:
            h, serialized = _compute_today_schedule_serialized()
            loop = asyncio.get_event_loop()
            loop.call_soon_threadsafe(asyncio.create_task, manager.broadcast(_schedule_message_from_serialized(serialized)))
    except Exception:
        pass
    return {"id": group.id, "name": group.name, "position_codes": group.position_codes}


@router.get("/api/v1/templates")
def list_templates(db: Session = Depends(get_db)):
    rows = db.scalars(select(TrainingTemplate).options(selectinload(TrainingTemplate.activities)).order_by(TrainingTemplate.id.asc())).all()
    return [_template_to_dict(row) for row in rows]


@router.post("/api/v1/templates", status_code=status.HTTP_201_CREATED)
def create_template(payload: dict, db: Session = Depends(get_db)):
    template = TrainingTemplate(
        name=payload["name"],
        valid_from=_parse_date(payload["valid_from"]),
        valid_to=_parse_date(payload["valid_to"]),
        weekday=int(payload["weekday"]),
        start_time=parse_time(payload["start_time"]),
        is_active=bool(payload.get("is_active", True)),
    )
    db.add(template)
    db.flush()

    for index, activity_payload in enumerate(payload.get("activities", [])):
        activity = ActivityTemplate(
            training_template_id=template.id,
            activity_type=activity_payload["activity_type"],
            duration_minutes=int(activity_payload["duration_minutes"]),
            topic=activity_payload.get("topic"),
            order_index=int(activity_payload.get("order_index", index)),
        )
        activity.position_codes = activity_payload.get("position_codes", [])
        activity.position_group_names = activity_payload.get("position_groups", [])
        db.add(activity)

    db.commit()
    db.refresh(template)
    template = db.scalar(select(TrainingTemplate).options(selectinload(TrainingTemplate.activities)).where(TrainingTemplate.id == template.id))
    # schedule changed -> trigger broadcast
    try:
        if database.SessionLocal is not None:
            h, serialized = _compute_today_schedule_serialized()
            loop = asyncio.get_event_loop()
            loop.call_soon_threadsafe(asyncio.create_task, manager.broadcast(_schedule_message_from_serialized(serialized)))
    except Exception:
        pass
    return _template_to_dict(template)


@router.patch("/api/v1/templates/{template_id}")
def patch_template(template_id: int, payload: dict, db: Session = Depends(get_db)):
    template = _require_template(db, template_id)

    if "name" in payload:
        template.name = payload["name"]
    if "valid_from" in payload:
        template.valid_from = _parse_date(payload["valid_from"])
    if "valid_to" in payload:
        template.valid_to = _parse_date(payload["valid_to"])
    if "weekday" in payload:
        template.weekday = int(payload["weekday"])
    if "start_time" in payload:
        template.start_time = parse_time(payload["start_time"])
    if "is_active" in payload:
        template.is_active = bool(payload["is_active"])

    db.commit()
    db.refresh(template)
    template = db.scalar(select(TrainingTemplate).options(selectinload(TrainingTemplate.activities)).where(TrainingTemplate.id == template.id))
    try:
        if database.SessionLocal is not None:
            h, serialized = _compute_today_schedule_serialized()
            loop = asyncio.get_event_loop()
            loop.call_soon_threadsafe(asyncio.create_task, manager.broadcast(_schedule_message_from_serialized(serialized)))
    except Exception:
        pass
    return _template_to_dict(template)


@router.post("/api/v1/templates/{template_id}/overrides", status_code=status.HTTP_201_CREATED)
def upsert_override(template_id: int, payload: dict, db: Session = Depends(get_db)):
    _require_template(db, template_id)
    override_date = _parse_date(payload["date"])

    override = db.scalar(
        select(TrainingOverride).where(
            TrainingOverride.training_template_id == template_id,
            TrainingOverride.date == override_date,
        )
    )
    if override is None:
        override = TrainingOverride(training_template_id=template_id, date=override_date)
        db.add(override)

    if "cancelled" in payload:
        override.cancelled = bool(payload["cancelled"])
    if "start_time" in payload:
        override.start_time = parse_time(payload["start_time"]) if payload["start_time"] else None
    if "activities" in payload:
        override.activities_json = json.dumps(payload["activities"])

    db.commit()
    db.refresh(override)
    try:
        if database.SessionLocal is not None:
            h, serialized = _compute_today_schedule_serialized()
            loop = asyncio.get_event_loop()
            loop.call_soon_threadsafe(asyncio.create_task, manager.broadcast(_schedule_message_from_serialized(serialized)))
    except Exception:
        pass
    return {"id": override.id, "template_id": template_id, "date": override.date.isoformat()}


@router.post("/api/v1/instances/adhoc", status_code=status.HTTP_201_CREATED)
def create_adhoc_instance(payload: dict, db: Session = Depends(get_db)):
    row = AdHocTrainingInstance(
        name=payload["name"],
        date=_parse_date(payload["date"]),
        start_time=parse_time(payload["start_time"]),
        activities_json=json.dumps(payload.get("activities", [])),
    )
    db.add(row)
    db.commit()
    db.refresh(row)
    try:
        if database.SessionLocal is not None:
            h, serialized = _compute_today_schedule_serialized()
            loop = asyncio.get_event_loop()
            loop.call_soon_threadsafe(asyncio.create_task, manager.broadcast(_schedule_message_from_serialized(serialized)))
    except Exception:
        pass
    return {"id": row.id, "name": row.name, "date": row.date.isoformat()}


@router.get("/api/v1/schedule")
def get_schedule(
    from_value: str = Query(..., alias="from"),
    to_value: str = Query(..., alias="to"),
    db: Session = Depends(get_db),
):
    from_date = _parse_date(from_value)
    to_date = _parse_date(to_value)
    if from_date > to_date:
        raise HTTPException(status_code=400, detail="'from' muss <= 'to' sein.")

    items = build_schedule(db, from_date, to_date)
    return {"ok": True, "items": items, "count": len(items)}


@router.websocket("/ws/live")
async def websocket_live(websocket: WebSocket):
    # optional token check: either query param `token` or header `x-ws-token`
    token = websocket.query_params.get("token") or websocket.headers.get("x-ws-token")
    cfg = websocket.app.state.config
    required = getattr(cfg, "WS_AUTH_TOKEN", None)
    if required:
        if not token or token != required:
            await websocket.close(code=1008)
            return

    await manager.connect(websocket)
    try:
        # send initial schedule for today
        if database.SessionLocal is not None:
            db = database.SessionLocal()
            try:
                today = datetime.utcnow().date()
                items = build_schedule(db, today, today)
                await manager.send_json(websocket, {"ok": True, "items": items, "count": len(items)})
            finally:
                db.close()

        # keep connection alive and periodically push updates
        last_hash = None
        while True:
            try:
                await asyncio.sleep(30)
                # compute today's schedule and only send if changed
                try:
                    if database.SessionLocal is None:
                        continue
                    h, serialized = _compute_today_schedule_serialized()
                    if h != last_hash:
                        last_hash = h
                        msg = _schedule_message_from_serialized(serialized)
                        await manager.send_json(websocket, msg)
                except Exception:
                    # on error, continue loop
                    continue
            except asyncio.CancelledError:
                break
    except WebSocketDisconnect:
        manager.disconnect(websocket)
    finally:
        manager.disconnect(websocket)
