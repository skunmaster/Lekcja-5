from src.models import Apartment, Bill, Parameters, Tenant, Transfer, ApartmentSettlement, TenantSettlement


class Manager:
    def __init__(self, parameters: Parameters):
        self.parameters = parameters 

        self.apartments = {}
        self.tenants = {}
        self.transfers = []
        self.bills = []
       
        self.load_data()

    def load_data(self):
        self.apartments = Apartment.from_json_file(self.parameters.apartments_json_path)
        self.tenants = Tenant.from_json_file(self.parameters.tenants_json_path)
        self.transfers = Transfer.from_json_file(self.parameters.transfers_json_path)
        self.bills = Bill.from_json_file(self.parameters.bills_json_path)

    def check_tenants_apartment_keys(self) -> bool:
        for tenant in self.tenants.values():
            if tenant.apartment not in self.apartments:
                return False
        return True
    
    def get_apartment_costs(self, apartment_key: str, year = None , month = None ) -> float | None:
        if apartment_key not in self.apartments:
            return None

        filtered_bills = [
            bill for bill in self.bills
            if bill.apartment == apartment_key
            and (year == 0 or bill.settlement_year == year or year is None)
        and (month == 0 or bill.settlement_month == month or month is None)
        ]

        if not filtered_bills:
            return 0.0

        total = sum(bill.amount_pln for bill in filtered_bills)
        return float(total)
    
    def create_apartment_settlement(self, apartment_key: str, year: int, month: int) -> ApartmentSettlement | None:
        if apartment_key not in self.apartments:
            return None

        bills_sum = self.get_apartment_costs(apartment_key, year, month)
        if bills_sum is None:
            bills_sum = 0.0

        transfers_sum = 0.0
        calculated_balance = float(transfers_sum - bills_sum)

        return ApartmentSettlement(
            apartment=apartment_key,
            year=year,
            month=month,
            total_rent_pln=0.0,
            total_bills_pln=bills_sum,
            total_due_pln=calculated_balance
        )
    
    def create_tenant_settlements(self, apartment_settlement: ApartmentSettlement) -> list[TenantSettlement]:
        apartment_key = apartment_settlement.apartment
        
        apartment_tenants_keys = [
            t_key for t_key, t_val in self.tenants.items() 
            if t_val.apartment == apartment_key
        ]
        
        num_tenants = len(apartment_tenants_keys)
        
        if num_tenants == 0:
            return []
            
        bills_share = float(apartment_settlement.total_bills_pln / num_tenants)
        due_share = float(apartment_settlement.total_due_pln / num_tenants)
        
        tenant_settlements = []
        for t_key in apartment_tenants_keys:
            ts = TenantSettlement(
                tenant=t_key,
                apartment_settlement=apartment_key,
                month=apartment_settlement.month,
                year=apartment_settlement.year,
                rent_pln=0.0,
                bills_pln=bills_share,
                balance_pln=due_share,
                total_due_pln=due_share
            )
            tenant_settlements.append(ts)
            
        return tenant_settlements