import os
import cv2
from PIL import Image, ImageChops
from skimage.metrics import structural_similarity


__pathBase = os.path.join(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")), "static")
__path = os.path.join(__pathBase, "report")

def create_image_old(clear_path: str, dirty_path: str)-> str:
    clear_image = Image.open(clear_path)
    dirty_image = Image.open(dirty_path)

    diff_image = ImageChops.difference(clear_image, dirty_image)
    path = os.path.join(__path, os.path.basename(dirty_path))

    if diff_image.getbbox():
        diff_image.save(path)
    else:
        dirty_image.save(path)

    return os.path.basename(path)


def create_image(clear_path: str, dirty_path: str) -> str:

    before = cv2.imread(clear_path)
    after = cv2.imread(dirty_path)
    path = os.path.join(__path, os.path.basename(dirty_path))

    before_gray = cv2.cvtColor(before, cv2.COLOR_BGR2GRAY)
    after_gray = cv2.cvtColor(after, cv2.COLOR_BGR2GRAY)

    (score, diff) = structural_similarity(before_gray, after_gray, full=True)
    diff = (diff * 255).astype("uint8")

    thresh = cv2.threshold(diff, 0, 255, cv2.THRESH_BINARY_INV | cv2.THRESH_OTSU)[1]
    contours = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    contours = contours[0] if len(contours) == 2 else contours[1]

    for c in contours:
        area = cv2.contourArea(c)
        if area > 55:
            x, y, w, h = cv2.boundingRect(c)
            cv2.rectangle(after, (x, y), (x + w, y + h), (36, 255, 12), 2)

    #cv2.imshow('after', after)
    cv2.imwrite(path, after)
    #cv2.waitKey()
    return os.path.basename(path)




if __name__ == '__main__':
    import os

    __pathBase = os.path.join(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")), "static")
    __path = os.path.join(__pathBase, "report")
    __path_for_raw_report = os.path.join(__pathBase, "raw_report")
    __path_for_flat = os.path.join(__pathBase, "flat")

    photos = [
        # (os.path.join(__path_for_flat, "clear_flat_1.png"), os.path.join(__path_for_raw_report, "dirty_flat_1.png")),
        # (os.path.join(__path_for_flat, "clear_flat_2.png"), os.path.join(__path_for_raw_report, "dirty_flat_2.png")),
        # (os.path.join(__path_for_flat, "clear_flat_3.png"), os.path.join(__path_for_raw_report, "dirty_flat_3.png")),
        # (os.path.join(__path_for_flat, "clear_1.png"), os.path.join(__path_for_raw_report, "dirty_1.png")),
        # (os.path.join(__path_for_flat, "clear_2.png"), os.path.join(__path_for_raw_report, "dirty_2.png")),
        # (os.path.join(__path_for_flat, "clear_3.png"), os.path.join(__path_for_raw_report, "dirty_3.png")),
        # (os.path.join(__path_for_flat, "clear_4.png"), os.path.join(__path_for_raw_report, "dirty_4.png")),
        # (os.path.join(__path_for_flat, "clear_5.png"), os.path.join(__path_for_raw_report, "dirty_5.png")),
        # (os.path.join(__path_for_flat, "clear_1.png"), os.path.join(__path_for_flat, "clear_1.png")),
        # (os.path.join(__path_for_flat, "clear_2.png"), os.path.join(__path_for_flat, "clear_2.png")),
        # (os.path.join(__path_for_flat, "clear_3.png"), os.path.join(__path_for_flat, "clear_3.png")),
        # (os.path.join(__path_for_flat, "clear_4.png"), os.path.join(__path_for_flat, "clear_4.png")),
        # (os.path.join(__path_for_flat, "clear_5.png"), os.path.join(__path_for_flat, "clear_5.png")),
    ]
    for c, d in photos:
        s = create_image(c, d)
        # clear = Image.open(c)
        # dirty = Image.open(d)
        #
        # diff = ImageChops.difference(clear, dirty)
        #
        # if diff.getbbox():
        #     diff.show()