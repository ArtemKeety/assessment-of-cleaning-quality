import os
import cv2
import numpy as np
from customlogger import LOGGER
from PIL import Image, ImageChops


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


def highlight_differences(imgA_path: str, imgB_path: str, min_area: int = 55) -> str:
    base_name = os.path.basename(imgB_path)
    path = os.path.join(__path, base_name)

    A = cv2.imread(imgA_path)
    B = cv2.imread(imgB_path)
    if A is None or B is None:
        LOGGER.error("A is None or B is None")
        return "default.gif"

    # 1) ORB ключевые точки
    orb = cv2.ORB_create(nfeatures=4000)
    grayA = cv2.cvtColor(A, cv2.COLOR_BGR2GRAY)
    grayB = cv2.cvtColor(B, cv2.COLOR_BGR2GRAY)

    kA, dA = orb.detectAndCompute(grayA, None)
    kB, dB = orb.detectAndCompute(grayB, None)
    if dA is None or dB is None:
        cv2.imwrite(path, B)
        LOGGER.error("Не удалось найти дескрипторы (слишком однотонные/размытые фото)")
        return base_name

    # 2) Матчинг
    bf = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=True)
    matches = bf.match(dA, dB)
    matches = sorted(matches, key=lambda x: x.distance)[:800]

    if len(matches) < 10:
        cv2.imwrite(path, B)
        LOGGER.error("Слишком мало совпадений для выравнивания")
        return base_name

    ptsA = np.float32([kA[m.queryIdx].pt for m in matches]).reshape(-1,1,2)
    ptsB = np.float32([kB[m.trainIdx].pt for m in matches]).reshape(-1,1,2)

    # 3) Гомография (B -> A)
    H, mask = cv2.findHomography(ptsB, ptsA, cv2.RANSAC, 5.0)
    if H is None:
        cv2.imwrite(path, B)
        LOGGER.error("Не удалось оценить гомографию")
        return base_name

    # 4) Варпим B под геометрию A
    hA, wA = A.shape[:2]
    B_aligned = cv2.warpPerspective(B, H, (wA, hA))

    # 5) Diff (absdiff проще и часто достаточно)
    diff = cv2.absdiff(A, B_aligned)
    diff_gray = cv2.cvtColor(diff, cv2.COLOR_BGR2GRAY)

    # подавим мелкий шум
    diff_gray = cv2.GaussianBlur(diff_gray, (5,5), 0)

    # бинаризация
    _, thresh = cv2.threshold(diff_gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

    # немного морфологии, чтобы склеить “пятна”
    kernel = np.ones((3,3), np.uint8)
    thresh = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, kernel, iterations=1)
    thresh = cv2.dilate(thresh, kernel, iterations=1)

    # контуры и подсветка на B_aligned (или на A)
    cnts, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    vis = B_aligned.copy()
    for c in cnts:
        area = cv2.contourArea(c)
        if area >= min_area:
            x, y, w, h = cv2.boundingRect(c)
            cv2.rectangle(vis, (x, y), (x+w, y+h), (36, 255, 12), 2)

    cv2.imwrite(path, vis)
    #cv2.imshow('photo', vis)
    #cv2.waitKey()
    return base_name




if __name__ == '__main__':
    import os

    __pathBase = os.path.join(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")), "static")
    __path = os.path.join(__pathBase, "report")
    __path_for_raw_report = os.path.join(__pathBase, "raw_report")
    __path_for_flat = os.path.join(__pathBase, "flat")

    photos = (
        # (os.path.join(__path_for_flat, "clear_flat_1.png"), os.path.join(__path_for_raw_report, "dirty_flat_1.png")),
        # (os.path.join(__path_for_flat, "clear_flat_2.png"), os.path.join(__path_for_raw_report, "dirty_flat_2.png")),
        # (os.path.join(__path_for_flat, "clear_flat_3.png"), os.path.join(__path_for_raw_report, "dirty_flat_3.png")),

        #(os.path.join(__path_for_flat, "clear_flat_3.png"), os.path.join(__path_for_raw_report, "dirty_5.png")),

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
    )

    for c, d in photos:
        s = highlight_differences(c, d)
        # clear = Image.open(c)
        # dirty = Image.open(d)
        #
        # diff = ImageChops.difference(clear, dirty)
        #
        # if diff.getbbox():
        #     diff.show()