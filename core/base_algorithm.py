from abc import ABC, abstractmethod
from core.base_problem import BaseProblem

class BaseAlgorithm(ABC):
    def __init__(self, problem: BaseProblem, population_size: int, max_iterations: int):
        self.problem = problem
        self.population_size = population_size
        self.max_iterations = max_iterations
        
        self.best_solution = None
        if problem.is_minimization:
            self.best_fitness = float('inf')
        else:
            self.best_fitness = float('-inf')

        self.convergence_curve = []

    @abstractmethod
    def initialize(self):
        pass

    @abstractmethod
    def optimize(self):
        pass

    def update_best_solution(self, current_solution, current_fitness):
        if self.problem.is_minimization:
            if current_fitness < self.best_fitness:
                self.best_fitness = current_fitness
                self.best_solution = current_solution.copy()
        else:
            if current_fitness > self.best_fitness:
                self.best_fitness = current_fitness
                self.best_solution = current_solution.copy()

    def get_results(self) -> dict:
        return {
            "best_solution": self.best_solution,
            "best_fitness": self.best_fitness,
            "convergence_curve": self.convergence_curve
        }