# The following file is useful to transfer a section common to all templates to a single base template and avoid code duplication
from login.models import *


def reg_user_context(request):
    reg_user = None
    if request.user.is_authenticated:
        reg_user = RegisteredUser.objects.get(user=request.user.id)
    return {"reg_user": reg_user}
