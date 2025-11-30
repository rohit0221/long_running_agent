from target_repo.src.domain.models import Item

class Calculator:
    def add(self, a: float, b: float) -> float:
        return a + b

    def subtract(self, a: float, b: float) -> float:
        return a - b

    def multiply(self, a: float, b: float) -> float:
        return a * b

    def divide(self, a: float, b: float) -> float:
        if b == 0:
            raise ValueError("Cannot divide by zero")
        return a / b

    def calculate_total(self, items: list[Item]) -> float:
        total = 0.0
        for item in items:
            total += item.total_cost()
        return total
