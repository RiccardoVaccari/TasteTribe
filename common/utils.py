import base64
from datetime import datetime
import io
import random
from PIL import Image, ImageDraw, ImageFont
import requests


INTERACTION_LIKE = 1
INTERACTION_DISLIKE = -1
def check_user_suspension(reg_user):
    suspension = reg_user.reg_user_status["is_suspended"]
    if suspension:
        suspension_end = datetime.strptime(reg_user.reg_user_status["suspension_end"], "%Y-%m-%d")
        if suspension_end <= datetime.now():
            reg_user.reg_user_status["is_suspended"] = False
            reg_user.reg_user_status["suspension_end"] = None
            reg_user.save()
            return False
        else:
            return True
    else:
        return False


def elaborate_interaction(interaction, created, interaction_type):
    user_interaction = 0
    if interaction_type == "like":
        
        user_interaction = 1
        if not created and interaction.interaction_liked == INTERACTION_LIKE:
            
            user_interaction = 0
    elif interaction_type == "dislike":
        user_interaction = -1
        if not created and interaction.interaction_liked == INTERACTION_DISLIKE:
            user_interaction = 0
    
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

def generate_avatar(initial, size=100):
    background_colors = ["#FF5733", "#095e0f", "#001a76", "#690076", "#ae3200", "#7a7a00"]
    bg_color = random.choice(background_colors)
    
    image = Image.new('RGB', (size, size), color=bg_color)
    font_size = int(size * 0.7)
    try:
        font = ImageFont.truetype("arial.ttf", font_size)
    except IOError:
        font = ImageFont.load_default(font_size)
    
    draw = ImageDraw.Draw(image)
    draw.text((size/2, size/2), initial, font=font, fill="white", anchor='mm')
    
    return image


def image_to_base64(image):
    buffered = io.BytesIO()
    image.save(buffered, format="PNG")
    img_bytes = buffered.getvalue()
    img_base64 = base64.b64encode(img_bytes).decode('utf-8')
    
    return img_base64


def url_to_base64(url):
    try:
        response = requests.get(url)
        response.raise_for_status()
        base64_encoded = base64.b64encode(response.content)
        return base64_encoded.decode('utf-8')

    except requests.exceptions.RequestException as e:
        print(f"Errore nella richiesta: {e}")
        return None