
import pytest

from calculator import core


def test_add():
    assert core.add(1, 2) == 3


def test_subtract():
    assert core.subtract(5, 3) == 2


def test_multiply():
    assert core.multiply(3, 4) == 12


def test_divide():
    assert core.divide(8, 2) == 4


def test_divide_by_zero():
    with pytest.raises(ZeroDivisionError):
        core.divide(1, 0)
