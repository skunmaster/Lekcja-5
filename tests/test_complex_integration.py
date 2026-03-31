import pytest
from src.manager import Manager
from src.models import Parameters
from src.models import Bill
from src.models import ApartmentSettlement
from src.models import Tenant

def test_apartment_costs_with_optional_parameters():
    manager = Manager(Parameters())
    manager.bills.append(Bill(
        apartment='apart-polanka',
        date_due='2025-03-15',
        settlement_year=2025,
        settlement_month=2,
        amount_pln=1250.0,
        type='rent'
    ))

    manager.bills.append(Bill(
        apartment='apart-polanka',
        date_due='2024-03-15',
        settlement_year=2024,
        settlement_month=2,
        amount_pln=1150.0,
        type='rent'
    ))

    manager.bills.append(Bill(
        apartment='apart-polanka',
        date_due='2024-02-02',
        settlement_year=2024,
        settlement_month=1,
        amount_pln=222.0,
        type='electricity'
    ))

    costs = manager.get_apartment_costs('apartment-1', 2024, 1)
    assert costs is None

    costs = manager.get_apartment_costs('apart-polanka', 2024, 3)
    assert costs == 0.0

    costs = manager.get_apartment_costs('apart-polanka', 2024, 1)
    assert costs == 222.0

    costs = manager.get_apartment_costs('apart-polanka', 2025, 1)
    assert costs == 910.0
    
    costs = manager.get_apartment_costs('apart-polanka', 2024)
    assert costs == 1372.0

    costs = manager.get_apartment_costs('apart-polanka')
    assert costs == 3532.0

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

def test_get_apartment_costs_without_month():
    manager = Manager(Parameters())

    manager.bills.append(Bill(
        apartment='apart-polanka',
        date_due='2025-03-15',
        settlement_year=2025,
        settlement_month=2,
        amount_pln=1250.0,
        type='rent'
    ))

    manager.bills.append(Bill(
        apartment='apart-polanka',
        date_due='2024-03-15',
        settlement_year=2024,
        settlement_month=2,
        amount_pln=1150.0,
        type='rent'
    ))

    manager.bills.append(Bill(
        apartment='apart-polanka',
        date_due='2024-02-02',
        settlement_year=2024,
        settlement_month=1,
        amount_pln=222.0,
        type='electricity'
    ))

    total_2024 = manager.get_apartment_costs('apart-polanka', 2024, 0)  
    assert total_2024 == 1372.0  

    total_all = manager.get_apartment_costs('apart-polanka', 0, 0)  
    assert total_all == 3532.0  

def test_create_tenant_settlements():
    manager = Manager(Parameters())
    
    manager.tenants = {
        'tenant-1': Tenant(
            apartment='apart-2',
            room='room-1',
            name='Test 1',
            rent_pln=1000.0,
            deposit_pln=1000.0,
            date_agreement_from='2024-01-01',
            date_agreement_to='2024-12-31'
        ),
        'tenant-2': Tenant(
            apartment='apart-2',
            room='room-2',
            name='Test 2',
            rent_pln=1000.0,
            deposit_pln=1000.0,
            date_agreement_from='2024-01-01',
            date_agreement_to='2024-12-31'
        ),
        'tenant-3': Tenant(
            apartment='apart-1',
            room='room-1',
            name='Test 3',
            rent_pln=1000.0,
            deposit_pln=1000.0,
            date_agreement_from='2024-01-01',
            date_agreement_to='2024-12-31'
        )
    }

    apt_settlement_2 = ApartmentSettlement(
        apartment='apart-2', year=2024, month=6,
        total_rent_pln=0.0, total_bills_pln=600.0, total_due_pln=-600.0
    )
    
    ts_2 = manager.create_tenant_settlements(apt_settlement_2)
    
    assert ts_2 is not None
    assert len(ts_2) == 2  
    
    ts_2.sort(key=lambda x: x.tenant)
    
    assert ts_2[0].tenant == 'tenant-1'
    assert ts_2[0].year == 2024
    assert ts_2[0].month == 6
    assert ts_2[0].bills_pln == 300.0   
    assert ts_2[0].total_due_pln == -300.0
    
    assert ts_2[1].tenant == 'tenant-2'
    assert ts_2[1].year == 2024
    assert ts_2[1].month == 6
    assert ts_2[1].bills_pln == 300.0
    assert ts_2[1].total_due_pln == -300.0

    apt_settlement_1 = ApartmentSettlement(
        apartment='apart-1', year=2024, month=6,
        total_rent_pln=0.0, total_bills_pln=450.0, total_due_pln=-450.0
    )
    
    ts_1 = manager.create_tenant_settlements(apt_settlement_1)
    
    assert len(ts_1) == 1
    assert ts_1[0].tenant == 'tenant-3'
    assert ts_1[0].year == 2024
    assert ts_1[0].month == 6
    assert ts_1[0].bills_pln == 450.0
    assert ts_1[0].total_due_pln == -450.0

    apt_settlement_0 = ApartmentSettlement(
        apartment='apart-0', year=2024, month=6,
        total_rent_pln=0.0, total_bills_pln=100.0, total_due_pln=-100.0
    )
    
    ts_0 = manager.create_tenant_settlements(apt_settlement_0)
    
    assert isinstance(ts_0, list)
    assert len(ts_0) == 0