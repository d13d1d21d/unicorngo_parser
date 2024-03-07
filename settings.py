from __future__ import annotations
import json

class Settings:
    def __init__(self) -> None:
        self.raw = json.loads(open("settings.json").read())

    @property
    def csv_del(self) -> str:
        return self.raw.get("csv_del")
    
    @property
    def sizes(self) -> list[float]:
        return self.raw.get("sizes")
    
    @property
    def brands(self) -> list[str]:
        return self.raw.get("brands")
    
    @property
    def to_xlsx(self) -> bool:
        return self.raw.get("to_xlsx")
    
    @property
    def products(self) -> ProductsSettings:
        class ProductsSettings:
            def __init__(self, raw: dict[str, str]) -> None:
                self.raw = raw
            
            @property
            def chunk_size(self) -> str:
                return int(self.raw.get("chunk_size"))
            
            @property
            def threads(self) -> str:
                return int(self.raw.get("threads"))

        return ProductsSettings(self.raw.get("products"))
    
    @property
    def cards(self) -> CardsSettings:
        class CardsSettings:
            def __init__(self, raw: dict[str, str]) -> None:
                self.raw = raw
            
            @property
            def per_page(self) -> str:
                return int(self.raw.get("per_page"))

        return CardsSettings(self.raw.get("cards"))

settings = Settings()

    
    
    