from typing import override

from core.costs.cost_function import CostFunction


class ComputingEnergyCost(CostFunction):

    @override
    def calculate_cost(self, data_in: int, speed: float, energy_memory: float, energy_computing: float) -> float:
        return (energy_memory * data_in) + (energy_computing * (data_in / speed))