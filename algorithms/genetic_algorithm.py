import time
import copy
from core.base_algorithm import BaseAlgorithm
from core.base_problem import BaseProblem
from algorithms.utils import buat_solusi_awal, get_neighbor
import numpy as np

class GeneticAlgorithm(BaseAlgorithm):
    def __init__(self, problem: BaseProblem, population_size: int, max_iterations: int, 
                 crossover_rate: float = 0.8, mutation_rate: float = 0.2):
        super().__init__(problem, population_size, max_iterations)
        self.crossover_rate = crossover_rate
        self.mutation_rate = mutation_rate
        self.population = []
        self.fitness_scores = []
        self.run_time = 0.0

    def initialize(self):
        self.population = [buat_solusi_awal(self.problem.dataset) for _ in range(self.population_size)]

    def _evaluate_population(self):
        self.fitness_scores = [self.problem.evaluate(ind) for ind in self.population]

    def optimize(self, verbose: bool = False, print_interval: int = 10):
        start_time = time.time()
        self.initialize()
        
        for generation in range(1, self.max_iterations + 1):
            self._evaluate_population()
            
            best_idx = np.argmax(self.fitness_scores) # Karena maksimasi worst-off profit
            self.update_best_solution(self.population[best_idx], self.fitness_scores[best_idx])
            self.convergence_curve.append(self.best_fitness)

            new_population = [copy.deepcopy(self.best_solution)]
            
            while len(new_population) < self.population_size:
                parent = copy.deepcopy(np.random.choice(self.population))
                
                if np.random.rand() < self.mutation_rate:
                    parent = get_neighbor(parent, self.problem.dataset)
                    
                new_population.append(parent)
                    
            self.population = new_population
            
        self.run_time = time.time() - start_time

    def get_results(self) -> dict:
        results = super().get_results()
        results["run_time"] = self.run_time
        self.problem.evaluate(self.best_solution)
        results["overall_profit"] = self.problem.last_overall_profit
        return results