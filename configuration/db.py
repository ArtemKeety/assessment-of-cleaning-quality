import os
from .base import MAX_CONNECTIONS, MIN_CONNECTIONS, TIMEOUT
from dotenv import load_dotenv

load_dotenv()

class PsqlConfig:
    host = os.getenv('psql_host')
    port = int(os.getenv('psql_port'))
    user = os.getenv('psql_user')
    password = os.getenv('psql_pass')
    database = os.getenv('psql_bd_name')
    timeout = TIMEOUT
    max_size = MAX_CONNECTIONS
    min_size = MIN_CONNECTIONS

    def __str__(self):
        return f"postgresql://{self.user}:{self.password}@{self.host}:{self.port}/{self.database}"


class RedisConfig:
    host = os.getenv('redis_host')
    port = int(os.getenv('redis_port'))
    db = int(os.getenv('redis_db_number'))
    decode_responses = False
    max_connections = MAX_CONNECTIONS

    def __str__(self) -> str:
        return f"redis://{self.host}:{self.port}/{self.db}"

