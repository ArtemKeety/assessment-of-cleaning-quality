import os

FILE_SIZE = 10 * 1024 * 1024
__BASE_FILE_PATH = os.path.join(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")), "static")
FLAT_FILE_PATH = os.path.join(__BASE_FILE_PATH, "flat")
REPORT_FILE_PATH = os.path.join(__BASE_FILE_PATH, "report")
RAW_REPORT_FILE_PATH = os.path.join(__BASE_FILE_PATH, "raw_report")

