import os
import time
from customlogger import LOGGER
from configuration import RAW_REPORT_FILE_PATH, REPORT_FILE_PATH, FLAT_FILE_PATH


def request_from_aiV2(report_id: int , dirty_photo: list[str], clear_photo: list[str]):
    LOGGER.info("worker is get")
    time.sleep(5)

    for d_obj, c_obj in zip(dirty_photo, clear_photo):
        LOGGER.info(f"dirty: {d_obj}, {os.path.exists(os.path.join(RAW_REPORT_FILE_PATH, d_obj))}")
        LOGGER.info(f"clear: {c_obj}, {os.path.exists(os.path.join(FLAT_FILE_PATH, c_obj))}")

        time.sleep(5)
    LOGGER.info("worker is done")