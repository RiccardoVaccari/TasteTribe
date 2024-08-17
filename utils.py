from datetime import datetime

def check_user_suspension(reg_user):
    suspension = reg_user.reg_user_status["is_suspended"]
    # Check whether to remove suspension if it ended
    if suspension:
        suspension_end = datetime.strptime(reg_user.reg_user_status["suspension_end"], "%Y-%m-%d")
        if suspension_end <= datetime.now():
            # Suspension ended so we reset the user status
            reg_user.reg_user_status["is_suspended"] = False
            reg_user.reg_user_status["suspension_end"] = None
            reg_user.save()
            return False
        else:
            return True
    else:
        return False