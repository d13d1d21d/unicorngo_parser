from proxy_client import ProxyClient
from utils import *
from dataclasses import dataclass
from colorthief import ColorThief


@dataclass
class ProductData:
    url: str
    sku: str
    spu: str
    name: str
    brand: str
    category: str
    price: int
    in_stock: int
    color: str
    size: str
    images: list[str]
    description: str


class Parser:
    BASE = "https://unicorngo.ru/api/catalog/product"

    def __init__(self, proxy_client: ProxyClient) -> None:
        self.proxy_client = proxy_client

    @staticmethod
    def product_url(sku: str, slug: str, spu: str) -> str:
        return f"https://unicorngo.ru/product/{slug}-{spu}?sku={sku}"
    
    @debug("Ошибка в парсинге SPU для {brand} - {size}: стр. {page}", True)
    def get_spus(self, page: int, size: float, brand: str) -> list[int]:
        if data := self.proxy_client.retry("GET", self.BASE + f"?category=sneakers&perPage=1000&page={page}&sizeType=EU&sort=by-relevance&sizeValue={size}&brands={brand}"):
            return list(
                i.get("spuId")
                for i in data.json().get("items", [])
            )
    
    @debug("Ошибка в товарв: {spu_data}")
    def get_product_data(self, spu_data: list[str]) -> list[ProductData]:
        v = []

        if data := self.proxy_client.retry("GET", self.BASE + f"/{spu_data[0]}").json():
            slug = data.get("slug")
            name = data.get("name")
            category = list(data.get("category").values())[-1]
            desc = data.get("description", "-").replace("\n", "")
            images = data.get("skus")[0].get("images")
            brand = spu_data[1]
            color = dom_color_name(
                *ColorThief(
                    self.proxy_client.retry("GET", f"https://image.unicorngo.ru/_next/image?url={images[0]}&w=128&q=75", stream=True).raw
                ).get_color(10)
            )

            for i in data.get("skus"):
                if (price := i.get("price")) > 0:
                    v.append(
                        ProductData(
                            self.product_url(i.get("skuId"), slug, spu_data[0]),
                            str(i.get("skuId")), 
                            spu_data[0],
                            name,
                            brand,
                            category,
                            str(price),
                            2,
                            color,
                            i.get("size").get("primary"),
                            images,
                            desc
                        )
                    )

        return v