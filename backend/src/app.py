from fastapi import FastAPI, HTTPException
import logging

from tweets_api.routes import router as r1
from users_api.routes import router as r2
from medias_api.routes import router as r3
from main_api.routes import router as r4
from handlers import http_exception_handler


def init_app():
    """
    Factory for FastAPI, where WSGI app is initialized and applies all configurations.

    :return: instance of FastAPI
    """
    app = FastAPI(debug=True)

    app.include_router(r1, prefix="/api/tweets")
    app.include_router(r2, prefix="/api/users")
    app.include_router(r3, prefix="/api/medias")
    app.include_router(r4, prefix="/api")

    app.add_exception_handler(HTTPException, http_exception_handler)

    logging.info("FastAPI application initialized")

    return app
