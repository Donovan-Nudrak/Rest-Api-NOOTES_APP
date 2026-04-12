#!/usr/bin/env python3
"""Stable error/success codes (enums) and human-readable strings for JSON API responses."""

from enum import Enum

class UserErrors(str, Enum):

    REQUIRED_USER = "REQUIRED_USER"
    REQUIRED_USER_ID = "REQUIRED_USER_ID"
    REQUIRED_USERNAME = "REQUIRED_USERNAME"
    REQUIRED_EMAIL = "REQUIRED_EMAIL"
    REQUIRED_PASSWORD = "REQUIRED_PASSWORD"

    INVALID_PYALOAD = "INVALID_PYALOAD"
    INVALID_USER = "INVALID_USER"
    INVALID_USER_ID = "INVALID_USER_ID"
    INVALID_USERNAME = "INVALID_USERNAME"
    INVALID_EMAIL = "INVALID_EMAIL"
    INVALID_PASSWORD = "INVALID_PASSWORD"

    USER_NOT_FOUND = "USER_NOT_FOUND"
    EMAIL_NOT_FOUND = "EMAIL_NOT_FOUND"
    USER_ALREADY_EXISTS = "USER_ALREADY_EXISTS"
    EMAIL_ALREADY_EXISTS = "EMAIL_ALREADY_EXISTS"

    ACCESS_DENIED = "ACCESS_DENIED"


USER_ERROR_MESSAGES = {
    UserErrors.REQUIRED_USER_ID: "User id is required",
    UserErrors.REQUIRED_USER: "User is required.",
    UserErrors.REQUIRED_USERNAME: "Username is required.",
    UserErrors.REQUIRED_EMAIL: "Email is required.",
    UserErrors.REQUIRED_PASSWORD: "Password is required.",

    UserErrors.INVALID_PYALOAD: "Invalid Payload",
    UserErrors.INVALID_USER: "Invalid user.",
    UserErrors.INVALID_USER_ID: "Invalid user id",
    UserErrors.INVALID_USERNAME: "Invalid username.",
    UserErrors.INVALID_EMAIL: "Invalid email.",
    UserErrors.INVALID_PASSWORD: "Invalid password.",

    UserErrors.USER_NOT_FOUND: "User not found.",
    UserErrors.EMAIL_NOT_FOUND: "Email not found.",
    UserErrors.USER_ALREADY_EXISTS: "User already exists.",
    UserErrors.EMAIL_ALREADY_EXISTS: "Email already exists.",

    UserErrors.ACCESS_DENIED: "Access denied.",
}


def get_user_error_message(code: UserErrors) -> str:
    return USER_ERROR_MESSAGES.get(code, "Unknown user error.")


class UserSuccess(str, Enum):
    USER_CREATED = "USER_CREATED"
    USER_LOGGED_IN = "USER_LOGGED_IN"


USER_SUCCESS_MESSAGES = {
    UserSuccess.USER_CREATED: "User created successfully.",
    UserSuccess.USER_LOGGED_IN: "Login successfully.",
}


def get_user_success_message(code: UserSuccess) -> str:
    return USER_SUCCESS_MESSAGES.get(code, "User success.")


class NoteErrors(str, Enum):

    REQUIRED_TITLE = "REQUIRED_TITLE"
    REQUIRED_CONTENT = "REQUIRED_CONTENT"
    REQUIRED_NOTE_ID = "REQUIRED_NOTE_ID"
    REQUIRED_USER_ID = "REQUIRED_USER_ID"
    REQUIRED_TARGET_EMAIL = "REQUIRED_TARGET_EMAIL"

    INVALID_PYALOAD = "INVALID_PYALOAD"
    INVALID_TITLE = "INVALID_TITLE"
    INVALID_CONTENT = "INVALID_CONTENT"
    INVALID_NOTE_ID = "INVALID_NOTE_ID"
    INVALID_USER_ID = "INVALID_USER_ID"

    NOTE_NOT_FOUND = "NOTE_NOT_FOUND"
    USER_NOT_FOUND = "USER_NOT_FOUND"
    NOTE_ALREADY_SHARED = "NOTE_ALREADY_SHARED"

    ACCESS_DENIED = "ACCESS_DENIED"


NOTE_ERROR_MESSAGES = {
    NoteErrors.REQUIRED_TITLE: "Title is required.",
    NoteErrors.REQUIRED_CONTENT: "Content is required.",
    NoteErrors.REQUIRED_NOTE_ID: "Note ID is required.",
    NoteErrors.REQUIRED_USER_ID: "User ID is required.",
    NoteErrors.REQUIRED_TARGET_EMAIL: "Target email is required.",

    NoteErrors.INVALID_PYALOAD: "Invalid Payload",
    NoteErrors.INVALID_TITLE: "Invalid title.",
    NoteErrors.INVALID_CONTENT: "Invalid content.",
    NoteErrors.INVALID_NOTE_ID: "Invalid note ID.",
    NoteErrors.INVALID_USER_ID: "Invalid user ID.",

    NoteErrors.NOTE_NOT_FOUND: "Note not found.",
    NoteErrors.USER_NOT_FOUND: "User not found.",
    NoteErrors.NOTE_ALREADY_SHARED: "Note already shared with user.",

    NoteErrors.ACCESS_DENIED: "Access denied.",
}


def get_note_error_message(code: NoteErrors) -> str:
    return NOTE_ERROR_MESSAGES.get(code, "Unknown note error.")


class NoteSuccess(str, Enum):
    NOTE_CREATED = "NOTE_CREATED"
    NOTE_UPDATED = "NOTE_UPDATED"
    NOTE_DELETED = "NOTE_DELETED"
    NOTE_SHARED = "NOTE_SHARED"


NOTE_SUCCESS_MESSAGES = {
    NoteSuccess.NOTE_CREATED: "Note created successfully.",
    NoteSuccess.NOTE_UPDATED: "Note updated successfully.",
    NoteSuccess.NOTE_DELETED: "Note deleted successfully.",
    NoteSuccess.NOTE_SHARED: "Note shared successfully.",
}


def get_note_success_message(code: NoteSuccess) -> str:
    return NOTE_SUCCESS_MESSAGES.get(code, "Note success.")
