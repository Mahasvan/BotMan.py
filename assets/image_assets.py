from PIL import Image

from assets import internet_funcs


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
