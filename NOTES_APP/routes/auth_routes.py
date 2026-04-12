#!/usr/bin/env python3
"""JSON auth routes under /api/auth; login establishes a server-side session."""

from flask import Blueprint, request, jsonify, session
from services.auth_services import create_user, login_user

auth_bp = Blueprint('auth', __name__, url_prefix='/api/auth')

@auth_bp.route('/register', methods=['POST'])
def register():

    data = request.json or {}
    result = create_user(data)

    if not result["status"]:
        errors = result.get("errors")
        code = result.get("code")
        return jsonify({"errors": errors}), code

    code = result.get("code")
    message = result.get("message")
    return jsonify({"message": message}), code


@auth_bp.route('/login', methods=['POST'])
def login():

    data = request.json or {}
    result = login_user(data)

    if not result["status"]:
        errors = result.get("errors")
        code = result.get("code")
        return jsonify({"errors": errors}), code

    code = result.get("code")
    message = result.get("message")

    session["user_id"] = result["user_id"]  # cookie-backed session for later note routes
    return jsonify({"message": message}), code


