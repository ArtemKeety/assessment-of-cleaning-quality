import os
from dotenv import load_dotenv

load_dotenv()

class SwaggerCredential:
    login: str = os.environ["SWAGGER_LOGIN"]
    password: str = os.environ["SWAGGER_PASSWORD"]