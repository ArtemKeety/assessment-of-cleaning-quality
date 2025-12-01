from fastapi import Request


async def get_header_data(request: Request):
    return request.headers.get("User-Agent")


async def user_address(request: Request) -> str:
    if ip := request.headers.get("X-Forwarded-For"):
        return F"{ip.split(",")[0].strip()}:{request.headers.get("User-Agent")}"
    return f"{request.client.host}:{request.client.port}:{request.headers.get("User-Agent")}"