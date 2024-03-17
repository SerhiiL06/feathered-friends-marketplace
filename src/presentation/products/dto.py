from dataclasses import dataclass
from datetime import datetime


@dataclass
class PriceDTO:
    retail: float
    wholesale: float


@dataclass
class CommentDTO:
    title: str


@dataclass
class ReadCommentDTO:
    title: str
    created_at: datetime


@dataclass
class ProductDTO:
    title: str
    description: str
    price: PriceDTO
    category_titles: list[str]
    tags: list[str]


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


# @dataclass
# class CreateOrderDTO:
#     item_list
