import os
import re
import time
import requests
import orjson
import base64
from dotenv import load_dotenv
from functools import wraps
from customlogger import LOGGER

load_dotenv()

API_KEY = os.getenv("API_KEY")

def custom_retry(count:int, max_times: int):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            error = None
            chunk = max_times / count
            for i in range(count):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    error = e
                    LOGGER.error(f"{type(e).__name__}: {e}")
                    times = (i+1) * chunk
                    time.sleep(times)
            #raise Exception(error)
            return "не удалось чётко распознать фотографию, все минусы выделены на фото"
        return wrapper
    return decorator

def encoding_file(file: str)-> base64.b64encode:
    with open(file, "rb") as f:
        array = []
        while chunk := f.read(1024 * 1024):
            array.append(chunk)
        string = b"".join(array)
        return base64.b64encode(string).decode('utf-8')

def choice_type(path: str)-> str:
    match os.path.basename(path).split(".")[-1]:
        case "jpg":
            return "image/jpeg"
        case "png":
            return "image/png"
        case _:
            return "image/jpeg"

models = [
        "qwen/qwen2-vl-72b-instruct:free", #- 0
        "google/gemini-flash-1.5:free", # - 1
        "openai/gpt-4o-mini:free", # - 2
        "google/gemma-3-27b-it:free", # - 3
        "anthropic/claude-3-haiku:free", # - 4
        "google/gemini-2.0-flash-exp:free", # -/+ 5 large timeout
        'mistralai/mistral-small-3.1-24b-instruct:free', # - 6
        'google/gemini-pro-1.5', # - 7
        'openrouter/bert-nebulon-alpha', # + 8
        "nvidia/nemotron-nano-12b-v2-vl:free", #+ 9
    ]


@custom_retry(count=5, max_times=120)
def create_comment(s: requests.Session, clear: str, dirty: str):

    clear_image: base64.b64encode = encoding_file(clear)
    dirty_image: base64.b64encode = encoding_file(dirty)

    clear_mem_type: str = choice_type(clear)
    dirty_mem_type: str = choice_type(dirty)

    response = s.post(
        url="https://openrouter.ai/api/v1/chat/completions",
        headers={
            "Authorization": f"Bearer {API_KEY}",
            "Content-Type": "application/json",
        },
        data=orjson.dumps({
            "model": models[8],
            "messages": [
                {
                    "role": "user", #"system", #"user",
                    "content": [
                        {
                            "type": "text",
                            "text": (
                                # "Ты ассистент для оценки чистоты квартир."
                                # "У тебя есть ДВЕ фотографии:"
                                # "- первое фото — чистая квартира (эталон);"
                                # "- второе фото — оцениваемая квартира."
                                # "Отвечай ТОЛЬКО по шаблону ниже, на русском языке."
                                # "БЕЗ любых вступлений, пояснений, обращений и переводов строк."
                                # "Формат ответа СТРОГО один:"
                                # "Недостатки: [список через запятую]. Оценка: [число от 1 до 10]."
                                # "Рекомендации: [текст не более 100 символов]."
                                """
                                Ты ассистент для оценки чистоты квартир.
                                У тебя есть ДВЕ фотографии:
                                — первое фото — чистая квартира (эталон);
                                — второе фото — оцениваемая квартира.
                                Если изображения по теме НЕ совпадают 
                                (например, одно не является квартирой или предметы/обстановка принципиально разные),
                                отвечай строго так:"Недостатки: невозможно оценить — несоответствие изображений.
                                Оценка: 0. Рекомендации: загрузите корректные фото."
                                Если изображения совпадают по теме, отвечай ТОЛЬКО по шаблону ниже, на русском языке,
                                БЕЗ вступлений, пояснений, обращений и переводов строк.
                                Формат ответа строго один:
                                "Недостатки: [список через запятую].
                                Оценка: [число от 1 до 10].
                                Рекомендации: [текст не более 100 символов]."
                                """
                            )
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:{clear_mem_type};base64,{clear_image}",
                                "detail": "Чистая квартира"
                            }
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:{dirty_mem_type};base64,{dirty_image}",
                                "detail": "Грязная квартира"
                            }
                        }
                    ]
                }
            ],
            "max_tokens": 100,
            "temperature": 0.2,
            "top_p": 0.8,
        })
    )
    response.raise_for_status()

    data = orjson.loads(response.text)

    if code := data.get('error'):
        if code['code'] != 200:
            raise Exception(code['message'])

    return data['choices'][0]['message']['content']


if __name__ == "__main__":
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

    session = requests.Session()
    for c, d in photos:
        n = create_comment(session, c, d)
