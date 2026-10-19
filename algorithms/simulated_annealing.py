import time
import math
import random
from core.base_algorithm import BaseAlgorithm
from algorithms.utils import buat_solusi_awal, get_neighbor

class SimulatedAnnealing(BaseAlgorithm):
    def __init__(self, problem, initial_temp=10000.0, cooling_rate=0.99, min_temp=0.1, max_iterations=None):
        super().__init__(problem, population_size=1, max_iterations=max_iterations or 0)
        self.initial_temp = initial_temp
        self.cooling_rate = cooling_rate
        self.min_temp = min_temp

        if max_iterations:
            self.cooling_rate = (min_temp / initial_temp) ** (1.0 / max_iterations)
        self.run_time = 0.0

    def initialize(self):
        self.current_solution = buat_solusi_awal(self.problem.dataset)
        self.current_fitness = self.problem.evaluate(self.current_solution)
        self.update_best_solution(self.current_solution, self.current_fitness)
        self.convergence_curve.append(self.best_fitness)

    def optimize(self):
        start_time = time.time()
        self.initialize()
        
        temp = self.initial_temp
        
        while temp > self.min_temp:
            neighbor = get_neighbor(self.current_solution, self.problem.dataset)
            neighbor_fitness = self.problem.evaluate(neighbor)
            
            delta = neighbor_fitness - self.current_fitness
            
            if delta > 0:
                self.current_solution = neighbor
                self.current_fitness = neighbor_fitness
                self.update_best_solution(neighbor, neighbor_fitness)
            else:
                probabilitas = math.exp(delta / temp)
                if random.random() < probabilitas:
                    self.current_solution = neighbor
                    self.current_fitness = neighbor_fitness
                    
            self.convergence_curve.append(self.best_fitness)
            temp *= self.cooling_rate
            
        self.run_time = time.time() - start_time

    def get_results(self) -> dict:
        results = super().get_results()
        results["run_time"] = self.run_time
        
        self.problem.evaluate(self.best_solution)
        results["overall_profit"] = self.problem.last_overall_profit
        return results