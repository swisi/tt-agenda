from flask import Flask, jsonify, request

from tt_agenda_v2.application import authenticate_user


def register_routes(app: Flask) -> None:
    @app.get("/health/live")
    def health_live():
        return jsonify({"status": "ok", "service": "tt-agenda-v2"}), 200

    @app.get("/health/ready")
    def health_ready():
        return jsonify({"status": "ready"}), 200

    @app.post("/auth/login")
    def login():
        payload = request.get_json(silent=True) or {}
        username = payload.get("username", "")
        password = payload.get("password", "")

        user_repository = app.extensions["user_repository"]
        user = authenticate_user(user_repository, username=username, password=password)
        if user is None:
            return jsonify({"ok": False, "message": "Ungültiger Benutzername oder Passwort."}), 401

        return jsonify({"ok": True, "username": user.username, "role": user.role}), 200
