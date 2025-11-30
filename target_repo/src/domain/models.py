from dataclasses import dataclass

@dataclass
class Item:
    name: str
    price: float
    quantity: int

    def total_cost(self) -> float:
        return self.price * self.quantity
