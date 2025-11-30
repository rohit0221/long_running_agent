from target_repo.src.domain.models import Item
import pytest


def test_total_cost_basic():
    item = Item(name="Book", price=12.99, quantity=2)
    assert item.total_cost() == pytest.approx(25.98)


def test_mutability_affects_total_cost():
    item = Item(name="Pencil", price=0.5, quantity=4)
    assert item.total_cost() == pytest.approx(2.0)
    item.quantity = 6
    assert item.total_cost() == pytest.approx(3.0)
    item.price = 0.75
    assert item.total_cost() == pytest.approx(4.5)


def test_equality_and_repr():
    a = Item(name="Notebook", price=3.0, quantity=5)
    b = Item(name="Notebook", price=3.0, quantity=5)
    c = Item(name="Notebook", price=3.0, quantity=4)
    assert a == b
    assert a != c
    r = repr(a)
    assert "Item" in r
    assert "Notebook" in r
    assert "5" in r


def test_zero_quantity_cost_zero():
    item = Item(name="Eraser", price=1.5, quantity=0)
    assert item.total_cost() == pytest.approx(0.0)