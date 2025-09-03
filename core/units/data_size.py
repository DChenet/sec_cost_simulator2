from __future__ import annotations

class DataUnit(int):
    pass


class Data:
    def __init__(self, value: int):
        self.value = DataUnit(value)

    def data_in(self) -> DataUnit:
        return self.value

    def data_out(self, phi: float, alter=True) -> DataUnit:
        new_value = self.value * int(phi)
        if alter:
            self.value = new_value

        return new_value