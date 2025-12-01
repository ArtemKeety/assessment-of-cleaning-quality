import os
from PIL import Image, ImageChops

__pathBase = os.path.join(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")), "static")
__path = os.path.join(__pathBase, "report")

def create_image(clear_path: str, dirty_path: str)-> str:
    clear_image = Image.open(clear_path)
    dirty_image = Image.open(dirty_path)

    diff_image = ImageChops.difference(clear_image, dirty_image)
    path = os.path.join(__path, os.path.basename(dirty_path))

    if diff_image.getbbox():
        diff_image.save(path)
    else:
        dirty_image.save(path)

    return os.path.basename(path)


if __name__ == '__main__':
    import os

    __pathBase = os.path.join(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")), "static")
    __path = os.path.join(__pathBase, "report")
    __path_for_raw_report = os.path.join(__pathBase, "raw_report")
    __path_for_flat = os.path.join(__pathBase, "flat")

    photos = [
        (os.path.join(__path_for_flat, "clear_flat_1.png"), os.path.join(__path_for_raw_report, "dirty_flat_1.png")),
        (os.path.join(__path_for_flat, "clear_flat_2.png"), os.path.join(__path_for_raw_report, "dirty_flat_2.png")),
        (os.path.join(__path_for_flat, "clear_flat_3.png"), os.path.join(__path_for_raw_report, "dirty_flat_3.png")),
    ]
    for c, d in photos:
        s = image(c, d)
        # clear = Image.open(c)
        # dirty = Image.open(d)
        #
        # diff = ImageChops.difference(clear, dirty)
        #
        # if diff.getbbox():
        #     diff.show()