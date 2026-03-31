import pytest
from src.manager import Manager
from src.models import Parameters

def test_get_apartment_costs_no_such_apartment():
    params = Parameters()
    manager = Manager(params)

    result = manager.get_apartment_costs("X999", 2024, 1)
    assert result is None

def test_get_apartment_costs_no_bills_in_month():
    params = Parameters()
    manager = Manager(params)

    result = manager.get_apartment_costs("apart-polanka", 1900, 1)
    assert result == 0.0

def test_get_apartment_costs_sum_for_month():
    params = Parameters()
    manager = Manager(params)

    cost = manager.get_apartment_costs("apart-polanka", 2025, 1)
    assert cost == 910