#!/usr/bin/env python3
"""Note CRUD, listing (owned + shared), and share-by-email; all HTTP-facing codes live in return dicts."""

from sqlalchemy.exc import IntegrityError
from models.user import User
from models.note import Note
from database.db import db
from datetime import datetime
from utils.validators import validate_create_note, validate_update_note
from utils.logger import log_api_action
from utils.messages import (
    NoteErrors,
    NoteSuccess,
    get_note_error_message,
    get_note_success_message
)


def create_note(data: dict) -> dict:

    result = validate_create_note(data)

    if result is not True:
        errors = [get_note_error_message(e) for e in result]
        return {"status": False, "errors": errors, "code": 400}

    user_id = data.get('user_id')
    title = data.get('title')
    content = data.get('content')
    visibility = data.get('visibility', 'private')

    user = User.query.get(user_id)

    if not user:
        log_api_action(
            action="note_create_failed",
            user_id=user_id,
            status="FAILED",
            extra={"reason":"user_not_found"},
        )
        errors = get_note_error_message(NoteErrors.USER_NOT_FOUND) 
        return {"status": False, "errors": errors, "code": 404}

    note = Note(
        user_id=user_id,
        title=title,
        content=content,
        visibility=visibility
    )

    db.session.add(note)
    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()

        log_api_action(
            action="note_create_failed",
            user_id=user_id,
            status="FAILED",
            extra={"reason": "IntegrityError"}
        )

        return {"status": False, "errors": "IntegrityError", "code": 400}

    log_api_action(
        action="note_created",
        user_id=user_id,
        status="OK",
        extra={"note_id": note.id},
    )
    message = get_note_success_message(NoteSuccess.NOTE_CREATED)
    return {"status": True, "message": message, "code": 201, "note_id": note.id}


def _serialize_note(note: object) -> dict:
    """Shape returned by list/get/update success paths."""
    owner_username = note.user.username if note.user else None

    return {
        "id": note.id,
        "title": note.title,
        "content": note.content,
        "user_id": note.user_id,
        "owner_username": owner_username,
        "visibility": note.visibility,
        "created_at": note.created_at.isoformat() if note.created_at else None,
        "updated_at": note.updated_at.isoformat() if note.updated_at else None,
    }


def get_notes(user_id: str | None = None) -> list:

    if user_id is None:
        errors = get_note_error_message(NoteErrors.REQUIRED_USER_ID)
        return {"status": False, "errors": errors, "code": 400}

    owned_notes = Note.query.filter_by(user_id=user_id).all()
    shared_notes = (Note.query.join(Note.shared_with).filter(User.id == user_id).all())
    all_notes = {note.id: note for note in owned_notes + shared_notes}.values()  # dedupe if both match

    return [_serialize_note(note) for note in all_notes]


def share_note(data: dict) -> dict:

    note_id = data.get("note_id")
    target_email = data.get("target_email")
    owner_id = data.get("owner_id")

    if not note_id:
        errors = get_note_error_message(NoteErrors.REQUIRED_NOTE_ID)
        return {"status": False, "errors": errors, "code": 400}

    if not target_email:
        errors = get_note_error_message(NoteErrors.REQUIRED_TARGET_EMAIL)
        return {"status": False, "errors": errors, "code": 400}

    note = Note.query.get(note_id)
    target_user = User.query.filter_by(email=target_email).first()

    if not note:
        error = get_note_error_message(NoteErrors.NOTE_NOT_FOUND)
        return {"status": False, "errors": error, "code": 404}

    if note.user_id != owner_id:
        error = get_note_error_message(NoteErrors.ACCESS_DENIED)
        return {"status": False, "errors": error, "code": 401}

    if not target_user:
        error = get_note_error_message(NoteErrors.USER_NOT_FOUND)
        return {"status": False, "errors": error, "code": 404}

    if target_user in note.shared_with:
        error = get_note_error_message(NoteErrors.NOTE_ALREADY_SHARED)
        return {"status": False, "errors": error, "code": 400}

    note.shared_with.append(target_user)

    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()

        log_api_action(
            action="note_shared_failed",
            user_id=owner_id,
            status="FAILED",
            extra={"reason": "IntegrityError"}
        )

        return {"status": False, "errors": "IntegrityError", "code": 400}

    log_api_action(
        action="note_shared",
        user_id=owner_id,
        status="OK",
        extra={"note_id": note.id, "shared_with": target_email},
    )

    message = get_note_success_message(NoteSuccess.NOTE_SHARED)
    return {"status": True, "message": message, "code": 200, "note_id": note.id}


def get_note_for_user(user_id: str, note_id: str) -> dict | list:

    if not user_id:
        errors = get_note_error_message(NoteErrors.REQUIRED_USER_ID)
        return {"status": False, "errors": errors, "code": 400}

    if not note_id:
        errors = get_note_error_message(NoteErrors.REQUIRED_NOTE_ID)
        return {"status": False, "errors": errors, "code": 400}

    note = Note.query.get(note_id)

    if not note:
        errors = get_note_error_message(NoteErrors.NOTE_NOT_FOUND)
        return {"status": False, "errors": errors, "code": 404}

    is_owner = note.user_id == user_id
    is_shared = User.query.get(user_id) in note.shared_with

    if not is_owner and not is_shared:
        errors = get_note_error_message(NoteErrors.ACCESS_DENIED)
        return {"status": False, "errors": errors, "code": 401}

    return _serialize_note(note)


def update_note_for_user(user_id: str, note_id: str, data: dict) -> dict:

    if not user_id:
        errors = get_note_error_message(NoteErrors.REQUIRED_USER_ID)
        return {"status": False, "errors": errors, "code": 400}

    if not note_id:
        errors = get_note_error_message(NoteErrors.REQUIRED_NOTE_ID)
        return {"status": False, "errors": errors, "code": 400}

    result = validate_update_note(data)

    if result is not True:
        errors = [get_note_error_message(e) for e in result]
        return {"status": False, "errors": errors, "code": 400}

    note = Note.query.get(note_id)

    if not note:
        errors = get_note_error_message(NoteErrors.NOTE_NOT_FOUND)
        return {"status": False, "errors": errors, "code": 404}

    is_owner = note.user_id == user_id
    shared_user = User.query.get(user_id)
    is_shared_with = shared_user is not None and shared_user in note.shared_with

    if not is_owner and not is_shared_with:
        errors = get_note_error_message(NoteErrors.ACCESS_DENIED)
        return {"status": False, "errors": errors, "code": 401}

        log_api_action(
            action="note_update_denied",
            user_id=user_id,
            status="FAILED",
            extra={"reason": "invalid data"}
        )

    title = data.get("title")
    content = data.get("content")

    note.title = title
    note.content = content

    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()

        log_api_action(
            action="note_update_denied",
            user_id=user_id,
            status="DENIED",
            extra={"reason": "IntegrityError"}
        )

        return {"status": False, "errors": "IntegrityError", "code": 400}

    log_api_action(
        action="note_updated_success",
        user_id=user_id,
        status="OK", 
        extra={"note_id": note.id},
    )

    return _serialize_note(note)


def delete_note_for_user(user_id: str, note_id: str) -> dict:

    if not user_id:
        errors = get_note_error_message(NoteErrors.REQUIRED_USER_ID)
        return {"status": False, "errors": errors, "code": 400}

    if not note_id: 
        errors = get_note_error_message(NoteErrors.REQUIRED_NOTE_ID)
        return {"status": False, "errors": errors, "code": 400}

    note = Note.query.get(note_id)

    if not note:
        errors = get_note_error_message(NoteErrors.NOTE_NOT_FOUND)
        return {"status": False, "errors": errors, "code": 404}

    if note.user_id != user_id:  # only owner may delete; shared users cannot
        errors = get_note_error_message(NoteErrors.ACCESS_DENIED)
        return {"status": False, "errors": errors, "code": 401}

    db.session.delete(note)

    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()

        log_api_action(
            action="note_delete_denied",
            user_id=user_id,
            status="FAILED",
            extra={"reason": "IntegrityError"}
        )
 
        return {"status": False, "errors": "IntegrityError", "code": 400}

    log_api_action(
        action="note_deleted_success",
        user_id=user_id,
        status="OK",
        extra={"note_id": note_id},
    )
    message = get_note_success_message(NoteSuccess.NOTE_DELETED) 
    return {"status": True, "message": message, "code": 200, "note_id": note_id}
