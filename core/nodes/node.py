

class Node:
    def __init__(self, speed: float, phi: float):
        self.speed = speed
        self.phi = phi

    def process(self, data: int) -> int:
        return int(data * self.phi)

    def get_speed(self) -> float:
        return self.speed

    def set_speed(self, speed: float) -> None:
        self.speed = speed

    def get_phi(self) -> float:
        return self.speed

    def set_phi(self, phi: float) -> None:
        self.speed = phi