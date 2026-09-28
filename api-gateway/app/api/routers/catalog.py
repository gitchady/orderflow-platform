from typing import Any

from fastapi import APIRouter

from app.api_client import request_service
from app.config import settings


router = APIRouter(prefix="/products", tags=["products"])


@router.get("")
async def get_products() -> Any:
    return await request_service("GET", f"{settings.CATALOG_SERVICE_URL}/products")


@router.get("/{product_id}")
async def get_product(product_id: str) -> Any:
    return await request_service(
        "GET",
        f"{settings.CATALOG_SERVICE_URL}/products/{product_id}",
    )
