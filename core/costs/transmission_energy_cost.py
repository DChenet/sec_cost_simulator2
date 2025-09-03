from typing import override

from core.costs.cost_function import CostFunction


class TransmissionEnergyCost(CostFunction):

    @override
    def calculate_cost(self, data_in: int, speed: float, distance: float, energy: float) -> float:
        return distance * energy * float(data_in / int(speed))