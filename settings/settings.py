from __future__ import annotations
import json

class Settings:
    def __init__(self) -> None:
        self.raw = json.loads(open("settings/settings.json").read())
    
    @property
    def sizes(self) -> list[float]:
        return self.raw.get("sizes")
    
    @property
    def brands(self) -> list[str]:
        return self.raw.get("brands")

settings = Settings()

    
    
    