
import os
import time
import requests
from database import SyncPsql
from customlogger import LOGGER
from celery_app import celery_app
from .ai_handler import create_comment
from .eq_image import highlight_differences



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

    self.update_state(
        state="PROGRESS",
        meta={
            "step":0,
            "count":len(dirty_photo),
        }
    )
    db = SyncPsql()

    session = requests.Session()

    with db() as conn:
        conn.execute("SELECT * FROM report_part WHERE report_id = %s", (report_id, ))
        record = conn.fetchall()

        for idx, (d_obj, c_obj) in enumerate(zip(dirty_photo, clear_photo)):
            dirty = os.path.join(__path_for_raw_report, d_obj)
            clear = os.path.join(__path_for_flat, c_obj)

            comm = create_comment(session, clear, dirty)
            image_path = highlight_differences(clear, dirty)

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

            self.update_state(
                state="PROGRESS",
                meta={
                    "step": idx+1,
                    "count": len(dirty_photo),
                }
            )

            time.sleep(5)

    self.update_state(
        state="SUCCESS",
        meta={
            "step": len(dirty_photo),
            "count": len(dirty_photo),
        }
    )

    LOGGER.info("celery is done")
