from typing_extensions import override

from core.costs.cost_function import CostFunction

class TransmissionTimeCost(CostFunction):

    @override
    def calculate_cost(self, data_in: int, speed: float) -> float:
        return data_in / int(speed)

