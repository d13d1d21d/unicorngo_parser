from settings import settings
from proxy_client import *
from utils import *
from colorthief import ColorThief
from dataclasses import dataclass
import pandas as pd
import logging



logging.basicConfig(level=logging.INFO, filename="parser_logs.log", filemode="a", format="%(asctime)s %(levelname)s %(message)s", encoding="utf-16")

@dataclass
class Product:
    sku: str
    spu: str
    url: str
    name: str
    category: str
    brand: str
    price: float
    size: str
    desc: str
    imgs: list[str]
    color: str

@dataclass
class ProductCard:
    sku: str
    spu: str
    url: str
    price: int
    name: str
    brand: str
    imgs: list[str]
    available: bool


def log_info(n: int) -> None:
    logging.info(f"Режим: Полный. Обработано {n} товаров")

class WebParser:
    BASE = "https://unicorngo.ru/api/catalog/product"

    def __init__(self, proxy_client: ProxyClient, per_page: int) -> None:
        self.proxy_client = proxy_client
        self.per_page = per_page

    @staticmethod
    def form_product_url(sku: str, slug: str, spu: str) -> str:
        return f"https://unicorngo.ru/product/{slug}-{spu}?sku={sku}"

    def parse_cards(self, page: int, size: float, brand: str) -> list[ProductCard] | int:
        try:
            return list(
                ProductCard(
                    x.get("skuId"),
                    x.get("spuId"),
                    self.form_product_url(x.get("skuId"), x.get("slug"), x.get("spuId")),
                    int(x.get("price")),
                    x.get("name"),
                    x.get("brand"),
                    x.get("images"),
                    "Да" if x.get("availability") == "AVAILABLE" else "Нет"
                )

                for x in self.proxy_client.http("GET", self.BASE + f"?category=sneakers&perPage={settings.cards.per_page}&page={page}&sizeType=EU&sort=by-relevance&sizeValue={size}&brands={brand}").json().get("items", [])
            )
        except:
            logging.error(f"Режим: Карточки тавров. URL: {self.BASE + f"?category=sneakers&perPage={settings.cards.per_page}&page={page}&sizeType=EU&sort=by-relevance&sizeValue={size}&brands={brand}"}", exc_info=True)
            return -1
    
    def parse_product(self, card: ProductCard) -> list[Product]:
        try:
            variations = []
            data = self.proxy_client.http("GET", self.BASE + f"/{card.spu}").json()

            category = list(data.get("category").values())[-1]
            desc = data.get("description", "Описание в первоисточнике не указано").replace("\n", "")

            color = dom_color_name(
                *ColorThief(
                    self.proxy_client.http("GET", f"https://image.unicorngo.ru/_next/image?url={card.imgs[0]}&w=128&q=75", stream=True).raw
                ).get_color(10)
            )

            for i in data.get("skus"):
                if (price := int(i.get("price"))) > 0:
                    variations.append(
                        Product(
                            i.get("skuId"),
                            data.get("spuId"),
                            card.url.replace(card.sku, str(i.get("skuId"))),
                            card.name,
                            category,
                            card.brand,
                            price,
                            i.get("size").get("primary"),
                            desc,
                            card.imgs,
                            color
                        )
                    )

            return variations
        except:
            logging.error(f"Режим: Полный. URL: {card.url}", exc_info=True)

def form_dataframe(products: list[Product | ProductCard], mode: str) -> pd.DataFrame:
    if mode == "cards":
        data = {
            "Артикул": [],
            "Объединяющий артикул": [],
            "URL": [],
            "Стоимость": [],
            "Название": [],
            "Бренд": [],
            "Изображения": [],
            "В наличии": []
        }
        for i in products:
            data["Артикул"].append(i.sku)
            data["Объединяющий артикул"].append(i.spu)
            data["URL"].append(i.url)
            data["Стоимость"].append(i.price)
            data["Название"].append(i.name)
            data["Бренд"].append(i.brand)
            data["Изображения"].append(";".join(i.imgs))
            data["В наличии"].append(i.available)
    else:
        data = {
            "Артикул": [],
            "Объединяющий артикул": [],
            "URL": [],
            "Название": [],
            "Категория": [],
            "Бренд": [],
            "Стоимость": [],
            "Размер": [],
            "Описание": [],
            "Изображения": [],
            "Цвет": []
        }
        for i in products:
            data["Артикул"].append(i.sku)
            data["Объединяющий артикул"].append(i.spu)
            data["URL"].append(i.url)
            data["Название"].append(i.name)
            data["Категория"].append(i.category)
            data["Бренд"].append(i.brand)
            data["Стоимость"].append(i.price)
            data["Размер"].append(i.size)
            data["Описание"].append(i.desc)
            data["Изображения"].append(";".join(i.imgs))
            data["Цвет"].append(i.color)

    return pd.DataFrame(data)