from core.nodes.node import Node


class ComputingNode(Node):
    def __init__(self, speed: float, phi: float):
        super().__init__(speed, phi)

    def time_cost(self, data_in: int) -> float:
        return data_in / self.speed

    def energy_cost(self, data_in: int, energy_uptime: float, energy_io: float) -> float:
        return (energy_io * data_in) + (energy_uptime * (data_in / self.speed))


