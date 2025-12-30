import os
import cv2
import numpy as np
from customlogger import LOGGER


__pathBase = os.path.join(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")), "static")
__path = os.path.join(__pathBase, "report")


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

    if dA is None or dB is None or len(kA) < 10 or len(kB) < 10:
        cv2.imwrite(path, B)
        LOGGER.error("Не удалось найти дескрипторы/ключевые точки (слишком однотонные/размытые фото)")
        return base_name

    # 2) Матчинг: KNN + ratio test (устойчивее, чем crossCheck=True)
    bf = cv2.BFMatcher(cv2.NORM_HAMMING)
    raw = bf.knnMatch(dA, dB, k=2)

    good = []
    for pair in raw:
        if len(pair) < 2:
            continue
        m, n = pair
        if m.distance < 0.75 * n.distance:
            good.append(m)

    if len(good) < 12:
        cv2.imwrite(path, B)
        LOGGER.error(f"Слишком мало хороших совпадений для выравнивания: {len(good)}")
        return base_name

    ptsA = np.float32([kA[m.queryIdx].pt for m in good]).reshape(-1, 1, 2)
    ptsB = np.float32([kB[m.trainIdx].pt for m in good]).reshape(-1, 1, 2)

    # 3) Гомография (B -> A) + проверка inliers
    H, inlier_mask = cv2.findHomography(ptsB, ptsA, cv2.RANSAC, 3.0)
    if H is None or inlier_mask is None:
        cv2.imwrite(path, B)
        LOGGER.error("Не удалось оценить гомографию")
        return base_name

    inliers = int(inlier_mask.sum())
    if inliers < 10:
        cv2.imwrite(path, B)
        LOGGER.error(f"Плохая гомография: слишком мало inliers = {inliers}")
        return base_name

    # 4) Варпим B под геометрию A
    hA, wA = A.shape[:2]
    B_aligned = cv2.warpPerspective(B, H, (wA, hA))

    # Маска валидной области после warp (чтобы не считать "чёрные поля" разницей)
    maskB = np.ones(B.shape[:2], dtype=np.uint8) * 255
    maskB_aligned = cv2.warpPerspective(maskB, H, (wA, hA))

    # 5) Diff
    diff = cv2.absdiff(A, B_aligned)
    diff_gray = cv2.cvtColor(diff, cv2.COLOR_BGR2GRAY)

    # учитывать только валидную часть
    diff_gray = cv2.bitwise_and(diff_gray, diff_gray, mask=maskB_aligned)

    # подавим шум
    diff_gray = cv2.GaussianBlur(diff_gray, (5, 5), 0)

    # ВАЖНО: фиксированный threshold часто стабильнее, чем Otsu (который может "всё сделать белым")
    _, thresh = cv2.threshold(diff_gray, 25, 255, cv2.THRESH_BINARY)

    # морфология: склеить пятна, убрать мелочь
    kernel = np.ones((3, 3), np.uint8)
    thresh = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, kernel, iterations=1)
    thresh = cv2.dilate(thresh, kernel, iterations=1)

    cnts, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    vis = B_aligned.copy()

    # защита: если контур огромный — скорее всего выравнивание/порог "поплыл"
    max_box_area = 0.60 * (hA * wA)

    for c in cnts:
        area = cv2.contourArea(c)
        if area < min_area:
            continue

        x, y, w, h = cv2.boundingRect(c)

        # пропускаем слишком большие регионы (типичный случай "выделило всё изображение")
        if (w * h) > max_box_area:
            continue

        cv2.rectangle(vis, (x, y), (x + w, y + h), (36, 255, 12), 2)

    cv2.imwrite(path, vis)
    # cv2.imshow('photo', vis)
    # cv2.waitKey()
    return base_name



if __name__ == '__main__':
    import os

    __pathBase = os.path.join(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")), "static")
    __path = os.path.join(__pathBase, "report")
    __path_for_raw_report = os.path.join(__pathBase, "raw_report")
    __path_for_flat = os.path.join(__pathBase, "flat")

    photos = (
        (os.path.join(__path_for_flat, "clear_flat_1.png"), os.path.join(__path_for_raw_report, "dirty_flat_1.png")),
        (os.path.join(__path_for_flat, "clear_flat_2.png"), os.path.join(__path_for_raw_report, "dirty_flat_2.png")),
        (os.path.join(__path_for_flat, "clear_flat_3.png"), os.path.join(__path_for_raw_report, "dirty_flat_3.png")),

        #(os.path.join(__path_for_flat, "clear_flat_3.png"), os.path.join(__path_for_raw_report, "dirty_5.png")),

        (os.path.join(__path_for_flat, "clear_1.png"), os.path.join(__path_for_raw_report, "dirty_1.png")),
        (os.path.join(__path_for_flat, "clear_2.png"), os.path.join(__path_for_raw_report, "dirty_2.png")),
        (os.path.join(__path_for_flat, "clear_3.png"), os.path.join(__path_for_raw_report, "dirty_3.png")),
        (os.path.join(__path_for_flat, "clear_4.png"), os.path.join(__path_for_raw_report, "dirty_4.png")),
        (os.path.join(__path_for_flat, "clear_5.png"), os.path.join(__path_for_raw_report, "dirty_5.png")),

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