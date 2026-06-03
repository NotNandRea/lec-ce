from PIL import Image, ImageOps

PROFILE_IMG_HEIGHT = 300

def is_image(file):
    try:
        file.seek(0) #reset image pointer
        img = Image.open(file)
        state=img.format in ["jpeg", "png", "jpg"]
        
        file.seek(0) #reset image pointer
        width, height = img.size

        if width < 300 or height < 300:
            file.seek(0)
            state=False
        file.seek(0) #reset image pointer
        

        return state
    except:
        return False

def to_square(image):

    #resizes the image to a square
    img = ImageOps.fit(img,(PROFILE_IMG_HEIGHT, PROFILE_IMG_HEIGHT),Image.Resampling.LANCZOS, centering=(0.5, 0.5))