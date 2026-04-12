#!/usr/bin/env python3
"""Request body checks; each validator returns True or a list of error enum codes for the caller."""

import re
from utils.messages import UserErrors, NoteErrors

_USERNAME_RE = re.compile(r"^[A-Za-z0-9_]+$")

def validate_register(data: dict) -> list | bool:

    if not isinstance(data, dict):
        return [UserErrors.INVALID_PAYLOAD]

    username = data.get("username")
    email = data.get("email")
    password = data.get("password")

    data_errors = []

    if not username:
        data_errors.append(UserErrors.REQUIRED_USERNAME)

    if not email:
        data_errors.append(UserErrors.REQUIRED_EMAIL)

    if not password:
        data_errors.append(UserErrors.REQUIRED_PASSWORD)

    if data_errors:
        return data_errors

    format_errors = []

    length_valid = 10 <= len(password) <= 128
    has_lower = any(c.islower() for c in password)
    has_upper = any(c.isupper() for c in password)
    has_digit = any(c.isdigit() for c in password)
    has_symbol = any(not c.isalnum() for c in password)

    if not (length_valid and has_lower and has_upper and has_digit and has_symbol):
        format_errors.append(UserErrors.INVALID_PASSWORD)

    if not (isinstance(username, str) and 5 <= len(username) <= 64 and _USERNAME_RE.fullmatch(username)):
        format_errors.append(UserErrors.INVALID_USERNAME)

    if not isinstance(email, str):
        format_errors.append(UserErrors.INVALID_EMAIL)
    else:
        parts = email.split("@")
        if not (5 <= len(email) <= 254 and len(parts) == 2 and "." in parts[1]):
            format_errors.append(UserErrors.INVALID_EMAIL)

    if format_errors:
        return format_errors

    return True


def validate_login(data: dict) -> list | bool:

    if not isinstance(data, dict):
        return [UserErrors.INVALID_PAYLOAD]

    email = data.get("email")
    password = data.get("password")

    data_errors = []

    if not email:
        data_errors.append(UserErrors.REQUIRED_EMAIL)

    if not password:
        data_errors.append(UserErrors.REQUIRED_PASSWORD)

    if data_errors:
        return data_errors

    format_errors = []

    if not isinstance(email, str):
        format_errors.append(UserErrors.INVALID_EMAIL)
    else:
        parts = email.split("@")
        if not (5 <= len(email) <= 254 and len(parts) == 2 and "." in parts[1]):
            format_errors.append(UserErrors.INVALID_EMAIL)

    if not isinstance(password, str) or not (10 <= len(password) <= 128):
        format_errors.append(UserErrors.INVALID_PASSWORD)

    if format_errors:
        return format_errors

    return True


def validate_create_note(data: dict) -> list | bool:

    if not isinstance(data, dict):
        return [NoteErrors.INVALID_PAYLOAD]

    title = data.get("title")
    content = data.get("content")

    data_errors = []

    if not title:
        data_errors.append(NoteErrors.REQUIRED_TITLE)

    if not content:
        data_errors.append(NoteErrors.REQUIRED_CONTENT)

    if data_errors:
        return data_errors

    format_errors = []

    if not isinstance(title, str) or not (1 <= len(title) <= 100):
        format_errors.append(NoteErrors.INVALID_TITLE)

    if not isinstance(content, str) or not (1 <= len(content) <= 10000):
        format_errors.append(NoteErrors.INVALID_CONTENT)

    if format_errors:
        return format_errors

    return True


def validate_update_note(data: dict) -> list | bool:

    if not isinstance(data, dict):
        return [NoteErrors.INVALID_PAYLOAD]

    data_errors = []
    format_errors = []

    if "title" in data:
        title = data["title"]
        if not title:
            data_errors.append(NoteErrors.REQUIRED_TITLE)

    if "content" in data:
        content = data["content"]
        if not content:
            data_errors.append(NoteErrors.REQUIRED_CONTENT)

    if data_errors:
        return data_errors

    if "title" in data:
        title = data["title"]
        if not isinstance(title, str) or not (1 <= len(title) <= 100):
            format_errors.append(NoteErrors.INVALID_TITLE)

    if "content" in data:
        content = data["content"]
        if not isinstance(content, str) or not (1 <= len(content) <= 10000):
            format_errors.append(NoteErrors.INVALID_CONTENT)

    if format_errors:
        return format_errors

    return True
