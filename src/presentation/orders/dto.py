from dataclasses import dataclass


@dataclass
class CreateOrderDto:
    first_name: str
    last_name: str
    city: str
    zip_code: int
