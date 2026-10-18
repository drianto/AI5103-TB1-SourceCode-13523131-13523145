from abc import ABC, abstractmethod
import numpy as np

class BaseProblem(ABC):
    def __init__(self, num_dimensions: int, bounds: list, is_minimization: bool = True):
        self.num_dimensions = num_dimensions
        self.bounds = bounds
        self.is_minimization = is_minimization

    @abstractmethod
    def evaluate(self, solution: np.ndarray) -> float:
        pass