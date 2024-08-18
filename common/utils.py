from datetime import datetime


# Definition of useful constants
INTERACTION_LIKE = 1
INTERACTION_DISLIKE = -1


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


def elaborate_interaction(interaction, created, interaction_type):
    # Parameter to pass to the frontend in order to render dynamically the like/dislike icons
    user_interaction = 0
    if interaction_type == "like":
        # If the interaction is new, then color the icon
        user_interaction = 1
        if not created and interaction.interaction_liked == INTERACTION_LIKE:
            # If the interaction was already the same, outline the icon
            user_interaction = 0
    elif interaction_type == "dislike":
        user_interaction = -1
        if not created and interaction.interaction_liked == INTERACTION_DISLIKE:
            user_interaction = 0
    # Handle the interaction to change, add or delete
    if interaction_type == "like":
        if interaction.interaction_liked == INTERACTION_LIKE:
            interaction.delete()
        else:
            interaction.interaction_liked = INTERACTION_LIKE
            interaction.save()
    elif interaction_type == "dislike":
        if interaction.interaction_liked == INTERACTION_DISLIKE:
            interaction.delete()
        else:
            interaction.interaction_liked = INTERACTION_DISLIKE
            interaction.save()
    return user_interaction
