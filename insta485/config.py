"""Insta485 development configuration."""

import pathlib

APPLICATION_ROOT = "/"

SECRET_KEY = b'u\xa4\xa5\x0f\xf4j\xc7M\x15\x95\xb7))\xb9\x0f\x8f\x9c\xc5\xa6R:\xa7\xaa\xfa'
SESSION_COOKIE_NAME = "login"

INSTA485_ROOT = pathlib.Path(__file__).resolve().parent.parent
UPLOAD_FOLDER = INSTA485_ROOT / "var" / "uploads"
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif"}
MAX_CONTENT_LENGTH = 16 * 1024 * 1024
DATABASE_FILENAME = INSTA485_ROOT / "var" / "insta485.sqlite3"