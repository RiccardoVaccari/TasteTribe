# The following file is useful to transfer a section common to all templates to a single base template and avoid code duplication
from login.models import *


def reg_user_context(request):
    reg_user = None
    user_initial = None
    if request.user.is_authenticated:
        try:
            reg_user = request.user.registereduser
        except RegisteredUser.DoesNotExist:
            reg_user = RegisteredUser(user=request.user)
        if request.user.first_name:
            user_initial = request.user.first_name[0]
        else:
            user_initial = request.user.username[0]
    return {"reg_user": reg_user, "user_initial": user_initial}
