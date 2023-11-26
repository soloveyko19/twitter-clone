from fastapi.responses import JSONResponse
from fastapi import HTTPException, Request


async def http_exception_handler(request: Request, exc: HTTPException):
    response = {
        "result": False,
        "error_type": "HttpException",
        "error_message": exc.detail,
    }
    return JSONResponse(status_code=exc.status_code, content=response)
