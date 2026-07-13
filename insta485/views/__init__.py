"""Views, one for each Insta485 page."""

from insta485.views.index import show_index
from insta485.views.accounts import (
    show_auth,
    show_create,
    show_delete,
    show_edit,
    show_login,
    show_password,
)