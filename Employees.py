from TesGo import Till


class Employee:
    def __init__(self, name, role):
        self.name = name
        self.role = role


class TillOperator(Employee):
    def __init__(self, name, role):
        super().__init__(name, role)


class StoreManager(Employee):
    def __init__(self, name, role):
        super().__init__(name, role)


class StockController(Employee):
    def __init__(self, name, role):
        super().__init__(name, role)


class FinancialConsultant(Employee):
    def __init__(self, name, role):
        super().__init__(name, role)
