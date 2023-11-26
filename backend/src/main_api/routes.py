from fastapi import APIRouter
from fastapi.openapi.docs import get_swagger_ui_html

router = APIRouter()


@router.get("/docs")
async def get_swagger_docs():
    return get_swagger_ui_html(openapi_url="/openapi.yml", title="Twitter")
