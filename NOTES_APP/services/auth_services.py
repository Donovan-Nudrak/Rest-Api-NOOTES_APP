#!/usr/bin/env python3
"""User registration and login logic; returns dicts with status, HTTP code, and messages/errors."""

from sqlalchemy.exc import IntegrityError
from models.user import User
from database.db import db
from utils.security import hash_password, verify_password
from utils.validators import validate_register, validate_login
from utils.logger import log_api_action
from utils.messages import (
    UserErrors,
    UserSuccess,
    get_user_error_message,
    get_user_success_message
)


def create_user(data: dict) -> dict:

    result = validate_register(data)

    if result is not True:

        log_api_action(
            action="user_create_failed",
            user_id=None,
            status="FAILED",
            extra={"reason": "invalid_data"}
        )

        errors = [get_user_error_message(e) for e in result]
        return {"status": False, "errors": errors, "code": 400}

    username = data.get('username')
    email = data.get('email')
    password = data.get('password')

    password_hash = hash_password(password)

    user = User(username=username, email=email, password_hash=password_hash) 

    db.session.add(user)
    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()  # rare race: unique constraint hit despite prior validation

        existing_username = User.query.filter_by(username=username).first()
        existing_email = User.query.filter_by(email=email).first()

        conflict_fields = []

        if existing_username:
            conflict_fields.append(UserErrors.USER_ALREADY_EXISTS)
        if existing_email:
            conflict_fields.append(UserErrors.EMAIL_ALREADY_EXISTS)

        if conflict_fields:

            log_api_action(
                action="user_create_failed",
                user_id=None,
                status="FAILED",
                extra={"email": email, "username": username, "reason": "integrity_error"},
                )
            errors = [get_user_error_message(e) for e in conflict_fields]
            return {"status": False, "errors": errors, "code": 409}

    log_api_action(
        action="user_created",
        user_id=user.id,
        status="OK",
        extra={"email": email},
    )
    message = get_user_success_message(UserSuccess.USER_CREATED)
    return {"status": True, "message": message, "code": 201, "user_id": user.id}


def login_user(data: dict) -> dict:

    result = validate_login(data)

    if result is not True:
        errors = [get_user_error_message(e) for e in result]
        return {"status": False, "errors": errors, "code": 400}

    email = data.get('email')
    password = data.get('password')

    user = User.query.filter_by(email=email).first()

    if not user:
        errors = get_user_error_message(UserErrors.USER_NOT_FOUND)
        return {"status": False, "errors": errors, "code": 404}

    if not verify_password(password, user.password_hash):
        errors = get_user_error_message(UserErrors.INVALID_PASSWORD)
        return {"status": False, "errors": errors, "code": 401}


    log_api_action(
        action="user_login_success",
        user_id=user.id,
        status="OK",
        extra={"email": email},
    )
    message = get_user_success_message(UserSuccess.USER_LOGGED_IN)
    return {"status": True, "message": message, "code": 200, "user_id": user.id}
