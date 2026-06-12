from PIL import Image, ImageOps

from utilities.constants import PROFILE_IMG_HEIGHT, TOUR_PHOTO_IMG_HEIGHT, TOUR_PHOTO_IMG_WIDTH

def is_image(file):
    try:
        file.seek(0) #reset image pointer
        img = Image.open(file)
        state=img.format in ["JPEG", "PNG", "JPG"]
        
        file.seek(0) #reset image pointer
        
        return state
    except:
        return False

def is_squareable(image):
    image.seek(0) #reset image pointer
    img = Image.open(image)
    
    image.seek(0) #reset image pointer
    width, height = img.size

    if width < PROFILE_IMG_HEIGHT or height < PROFILE_IMG_HEIGHT:
        image.seek(0)
        return False
    return True

def to_square(image):

    image.seek(0) #reset image pointer
    img = Image.open(image)

    #resizes the image to a square
    img = ImageOps.fit(img,(PROFILE_IMG_HEIGHT, PROFILE_IMG_HEIGHT),Image.Resampling.LANCZOS, centering=(0.5, 0.5))

    image.seek(0) #reset image pointer

    return img

def is_16_9able(image):
    image.seek(0) #reset image pointer
    img = Image.open(image)

    image.seek(0) #reset image pointer
    width, height = img.size

    if width < TOUR_PHOTO_IMG_WIDTH or height < TOUR_PHOTO_IMG_HEIGHT:
        image.seek(0)
        return False
    return True

def to_16_9(image):

    image.seek(0) #reset image pointer
    img = Image.open(image)

    #resizes the image to a 16:9 ratio
    img = ImageOps.fit(img,(TOUR_PHOTO_IMG_WIDTH, TOUR_PHOTO_IMG_HEIGHT),Image.Resampling.LANCZOS, centering=(0.5, 0.5))

    image.seek(0) #reset image pointer

    return img