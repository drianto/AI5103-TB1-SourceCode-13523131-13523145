import time
from core.base_algorithm import BaseAlgorithm
from algorithms.utils import buat_solusi_awal, dapatkan_tetangga

class HillClimbing(BaseAlgorithm):
    def __init__(self, problem, max_iterations):
        super().__init__(problem, population_size=1, max_iterations=max_iterations)
        self.run_time = 0.0

    def initialize(self):
        self.current_solution = buat_solusi_awal(self.problem.dataset)
        self.current_fitness = self.problem.evaluate(self.current_solution)
        self.update_best_solution(self.current_solution, self.current_fitness)
        self.convergence_curve.append(self.best_fitness)

    def optimize(self):
        start_time = time.time()
        self.initialize()
        
        for _ in range(self.max_iterations):
            neighbor = dapatkan_tetangga(self.current_solution, self.problem.dataset)
            neighbor_fitness = self.problem.evaluate(neighbor)
            
            if neighbor_fitness >= self.current_fitness:
                self.current_solution = neighbor
                self.current_fitness = neighbor_fitness
                self.update_best_solution(neighbor, neighbor_fitness)
                
            self.convergence_curve.append(self.best_fitness)
            
        self.run_time = time.time() - start_time

    def get_results(self) -> dict:
        results = super().get_results()
        results["run_time"] = self.run_time
        
        self.problem.evaluate(self.best_solution)
        results["overall_profit"] = self.problem.last_overall_profit
        return results