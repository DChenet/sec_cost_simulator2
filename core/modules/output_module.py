from math import log10

from core.modules.module import Module


class OutputModule(Module):
    def __init__(self, speed: float):
        super().__init__(speed, 1)

    def time_cost(self, data_in: int) -> float:
        return data_in / self.speed

    def energy_cost(self, data_in: int, energy: float, distance: float) -> float:
        return log10(distance) * energy * (data_in / self.speed)


