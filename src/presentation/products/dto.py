from dataclasses import dataclass


@dataclass
class PriceDTO:
    retail: float
    wholesale: float


@dataclass
class ProductDTO:
    title: str
    description: str
    price: PriceDTO
    category_titles: list[str]
    tags: list[str]
