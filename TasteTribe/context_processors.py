# The following file is useful to transfer a section common to all templates to a single base template and avoid code duplication
from login.models import *


def reg_user_context(request):
    reg_user = None
    user_initial = None
    if request.user.is_authenticated:
        reg_user = RegisteredUser.objects.get(user=request.user.id)
        user_initial = request.user.first_name[0]
    return {"reg_user": reg_user, "user_initial": user_initial}
