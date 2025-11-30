import pytest

from target_repo.src.service.calculator import Calculator


class DummyItem:
    def __init__(self, cost):
        self._cost = cost

    def total_cost(self):
        return self._cost


def test_add():
    calc = Calculator()
    assert calc.add(1.0, 2.5) == 3.5


def test_subtract():
    calc = Calculator()
    assert calc.subtract(10, 3) == 7


def test_multiply():
    calc = Calculator()
    assert calc.multiply(-3, 4) == -12


def test_divide_normal():
    calc = Calculator()
    assert calc.divide(9, 3) == 3


def test_divide_by_zero_raises():
    calc = Calculator()
    with pytest.raises(ValueError):
        calc.divide(1, 0)


def test_calculate_total_empty():
    calc = Calculator()
    assert calc.calculate_total([]) == 0.0


def test_calculate_total_with_items():
    calc = Calculator()
    items = [DummyItem(1.0), DummyItem(2.0), DummyItem(3.0)]
    assert calc.calculate_total(items) == 6.0