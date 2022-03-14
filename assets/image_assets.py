import math

from PIL import Image

from assets import internet_funcs

"""
Change this below ascii_chars variable to include more levels of brightness. 
When changing, make sure that the characters are in descending order of brightness.
@ has the highest brightness, and the space has the lowest brightness in this list.
"""
ascii_chars = "@%#*+=-:. "
brightness_steps = math.ceil(255 / len(ascii_chars))


def superimpose_image(foreground_img, background_img, offset=(0, 0), mask_img=None, final_path="storage/final.png"):
    fg = Image.open(foreground_img)
    bg = Image.open(background_img)
    bg = bg.convert("RGBA")
    if mask_img:
        mask = Image.open(mask_img)
        fg = fg.convert("RGBA")
        mask = mask.convert("RGBA")
        bg.paste(fg, offset, mask)
    else:
        bg.paste(fg, offset)
    bg.save(final_path)
    return final_path


def resize_image(file_path, size: tuple):
    img = Image.open(file_path)
    img = img.resize(size)
    img.save(file_path)
    return file_path


async def save_image(img_url, file_path):
    image_data = await internet_funcs.get_binary(str(img_url))
    with open(file_path, "wb") as f:
        f.write(image_data)
    return file_path


def asciify_image(file_path, final_path="storage/asciify.txt"):
    img = Image.open(file_path).convert("L")  # Open and convert to grayscale
    width, height = img.size  # Fetch image dimensions
    pixels = img.getdata()  # Fetch colour details of individual pixels
    new_pixels = "".join([ascii_chars[x//brightness_steps] for x in pixels])  # Convert each pixel to ascii, based on brightness
    # Sample output of `x` will be (128, 255, 128, 200), where 200 is the brightness level with a maximum of 255
    final_string = "\n".join([new_pixels[i:i+width] for i in range(0, len(new_pixels), width)])  # split the pixels into rows

    with open(final_path, "w") as f:
        f.write(final_string)  # Write the final string to the file
    return final_path
