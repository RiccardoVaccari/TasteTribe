import base64
from datetime import datetime
import io
import random
from PIL import Image, ImageDraw, ImageFont


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

def generate_avatar(initial, size=100):

    # Definisci i colori di sfondo possibili
    background_colors = ["#FF5733", "#095e0f", "#001a76", "#690076", "#ae3200", "#7a7a00"]
    bg_color = random.choice(background_colors)
    
    # Crea un'immagine quadrata
    image = Image.new('RGB', (size, size), color=bg_color)
    
    # Definisci il font e la dimensione del testo
    # Assicurati di avere il percorso del font corretto o usa un font di default
    font_size = int(size * 0.7)
    try:
        font = ImageFont.truetype("arial.ttf", font_size)
    except IOError:
        font = ImageFont.load_default(font_size)

    # Crea un oggetto di disegno
    draw = ImageDraw.Draw(image)
    
    # Aggiungi il testo all'immagine
    draw.text((size/2, size/2), initial, font=font, fill="white", anchor='mm')
    
    return image


def image_to_base64(image):
    # Crea un buffer in memoria per l'immagine
    buffered = io.BytesIO()
    
    # Salva l'immagine nel buffer come PNG (puoi scegliere altri formati)
    image.save(buffered, format="PNG")
    
    # Ottieni i dati dell'immagine in bytes dal buffer
    img_bytes = buffered.getvalue()
    
    # Converte i bytes in una stringa Base64
    img_base64 = base64.b64encode(img_bytes).decode('utf-8')
    
    return img_base64

if __name__ == "__main__":
    with open("avatar.txt", "w") as f:
        f.write(image_to_base64(generate_avatar("R")))