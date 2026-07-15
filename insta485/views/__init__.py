"""Views, one for each Insta485 page."""

from insta485.views.index import show_index
from insta485.views.user import show_user
from insta485.views.accounts import (
    show_auth,
    show_create,
    show_delete,
    show_edit,
    show_login,
    show_password,
)

from insta485.views.following import (
    show_following,
    update_following,
)
from insta485.views.followers import show_followers
from insta485.views.explore import show_explore
from insta485.views.uploads import show_upload
from insta485.views.post import show_post