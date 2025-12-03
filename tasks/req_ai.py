
import os
import time
import requests
from database import SyncPsql
from customlogger import LOGGER
from celery_app import celery_app
from .eq_image import create_image
from .ai_handler import create_comment



__pathBase = os.path.join(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")), "static")
__path = os.path.join(__pathBase, "report")
__path_for_raw_report = os.path.join(__pathBase, "raw_report")
__path_for_flat = os.path.join(__pathBase, "flat")


@celery_app.task(
    bind=True,
    max_retries=3,
    default_retry_delay=180,
    ignore_result=True,
    autoretry_for=(requests.RequestException,)
)
def request_from_ai(self, report_id: int , dirty_photo: list[str], clear_photo: list[str]):
    LOGGER.info("celery is starting")
    db = SyncPsql()
    session = requests.Session()
    with db() as conn:
        conn.execute("SELECT * FROM report_part WHERE report_id = %s", (report_id, ))
        record = conn.fetchall()

        for idx, (d_obj, c_obj) in enumerate(zip(dirty_photo, clear_photo)):
            dirty = os.path.join(__path_for_raw_report, d_obj)
            clear = os.path.join(__path_for_flat, c_obj)
            LOGGER.debug(f"dirty: {d_obj}, {os.path.exists(dirty)}")
            LOGGER.debug(f"clear: {c_obj}, {os.path.exists(clear)}")
            comm = create_comment(session, clear, dirty)
            image_path = create_image(clear, dirty)

            photos_id, *_ = record[idx]
            conn.execute(
                """
                    UPDATE report_part SET
                    info = %s,
                    path = %s
                    WHERE id = %s
                """,
                (comm, image_path, photos_id)
            )
            LOGGER.debug(f"dirty: {d_obj}, is Done")
            LOGGER.debug(f"clear: {c_obj}, is Done")
            time.sleep(5)
            db.commit()

        LOGGER.info("celery is done")
