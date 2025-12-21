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

class CustomRetry:

    __slots__ = ('count', 'max_times')

    def __init__(self, count: int, max_times: int):
        self.count = count
        self.max_times = max_times

    def __call__(self, func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            error = None
            chunk = self.max_times / self.count
            for i in range(self.count):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    error = e
                    LOGGER.error(f"{type(e).__name__}: {e}")
                    times = (i + 1) * chunk
                    time.sleep(times)
            raise requests.RequestException(f"{type(error).__name__}: {error}")
        return wrapper

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

models = (
        "nvidia/nemotron-nano-12b-v2-vl:free",  # + 0
        'amazon/nova-2-lite-v1:free',  # 1
        "google/gemma-3-27b-it:free", # +/- 2 rate/limit
        'x-ai/grok-4.1-fast:free',  # +\- 3 (403 error)
        "google/gemini-2.0-flash-exp:free", # +/- 4 large timeout and rateLimiter
        'openrouter/bert-nebulon-alpha', # -/+ 5 / last Error
        'google/gemma-3-4b-it:free', # 6
        'google/gemma-3-12b-it:free', # 7
)


@CustomRetry(count=5, max_times=60)
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
            "model": models[0],
            "messages": [
                {
                    "role": "user", #"system", #"user",
                    "content": [
                        {
                            "type": "text",
                            "text": (
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
            "max_tokens": 1256,
            "temperature": 0.1,
            "top_p": 0.8,
            "include_reasoning": False,
            "reasoning": {
                "effort": "minimal"      # или "low"
            },
        })
    )
    response.raise_for_status()

    data = orjson.loads(response.text)

    if code := data.get('error'):
        if code['code'] != 200:
            raise Exception(code['message'])

    usage = data.get("usage", {})
    comp = usage.get("completion_tokens", 0)
    reasoning = usage.get("completion_tokens_details", {}).get("reasoning_tokens", 0)
    prompt = usage.get("prompt_tokens", 0)

    LOGGER.info(
        "Tokens: prompt=%s, completion=%s (reasoning=%s, answer≈%s)",
        prompt,
        comp,
        reasoning,
        comp - reasoning,
    )

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
        print(n)
