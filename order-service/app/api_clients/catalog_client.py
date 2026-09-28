import httpx


class CatalogClient:
    def __init__(self, base_url: str) -> None:
        self.base_url = base_url
    
    def get_product(self, product_id: str) -> dict:
        response = httpx.get(f"{self.base_url}/products/{product_id}")
        return response.json()
