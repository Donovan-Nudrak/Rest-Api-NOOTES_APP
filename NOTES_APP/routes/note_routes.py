#!/usr/bin/env python3
"""JSON note routes under /api/notes; user id comes from session (set at login)."""

from flask import Blueprint, request, jsonify, session
from services.note_services import (
    create_note,
    get_notes,
    share_note,
    get_note_for_user,
    update_note_for_user,
    delete_note_for_user,
)


note_bp = Blueprint('note', __name__, url_prefix='/api/notes')

@note_bp.route('/', methods=['GET'])
def list_notes():
    user_id = session.get("user_id")  # None when client sends no session cookie
    notes = get_notes(user_id=user_id)

    return jsonify(notes), 200


@note_bp.route('/create', methods=['POST'])
def new_note():
 
    data = request.json or {}

    data["user_id"] = session.get("user_id")

    result = create_note(data)

    if not result["status"]:
        errors = result.get("errors")
        code = result.get("code")
        return jsonify({"errors": errors}), code

    message = result.get("message")
    code = result.get("code")
    return jsonify({"message": message}), code


@note_bp.route('/share', methods=['POST'])
def share():

    user_id = session.get("user_id")

    data = request.json or {}

    data["owner_id"] = user_id

    result = share_note(data)

    if not result["status"]:
        errors = result.get("errors")
        code = result.get("code")
        return jsonify({"errors": errors}), code

    message = result.get("message")
    code = result.get("code")
    return jsonify({"message": message}), code


@note_bp.route('/<int:note_id>', methods=['GET'])
def get_note(note_id):

    user_id = session.get("user_id")

    result = get_note_for_user(user_id=user_id, note_id=note_id)

    if isinstance(result, dict) and result.get("status") is False:
        errors = result.get("errors")
        code = result.get("code")
        return jsonify({"errors": errors}), code

    code = 200
    return jsonify(result), code


@note_bp.route('/<int:note_id>', methods=['PUT'])
def update_note(note_id):
 
    user_id = session.get("user_id")
    data = request.json or {}

    result = update_note_for_user(user_id=user_id, note_id=note_id, data=data)

    if isinstance(result, dict):
        errors = result.get("errors")
        code = result.get("code")
        return jsonify({"errors": errors}), code

    code = 200
    return jsonify(result), code


@note_bp.route('/<int:note_id>', methods=['DELETE'])
def delete_note(note_id):

    user_id = session.get("user_id")

    result = delete_note_for_user(user_id=user_id, note_id=note_id)

    if not result["status"]:
        errors = result.get("errors")
        code = result.get("code")
        return jsonify({"errors": errors}), code

    message = result.get("message")
    code = result.get("code")
    return jsonify(message), code

