from dataclasses import dataclass
from datetime import datetime


@dataclass
class PriceDTO:
    retail: float
    wholesale: float


@dataclass
class CommentDTO:
    title: str
    text: str
    score: int


@dataclass
class ReadCommentDTO:
    title: str
    created_at: datetime


@dataclass
class ProductDTO:
    title: str
    description: str
    brand: str
    country: str
    price: PriceDTO
    category_titles: list[str]

    stock: int
    tags: list[str]


@dataclass
class ProductDTO:
    title: str = None
    description: str = None
    brand: str = None
    country: str = None
    price: PriceDTO = None
    category_titles: list[str] = None
    stock: int = None
    tags: list[str] = None


@dataclass
class DetailProductDTO:
    title: str
    description: str
    slug: str
    price: PriceDTO
    category_ids: list[str]
    tags: list[str]
    comments: list[ReadCommentDTO] = None


@dataclass
class FullProductDTO(PriceDTO):
    comments: list[ReadCommentDTO]
    votes: int
