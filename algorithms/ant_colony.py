import time
import numpy as np
from core.base_algorithm import BaseAlgorithm
from core.base_problem import BaseProblem

class AntColonyOptimization(BaseAlgorithm):
    def __init__(self, problem: BaseProblem, num_ants: int, max_iterations: int,
                 alpha: float = 1.0, beta: float = 2.0, evaporation_rate: float = 0.1, Q: float = 100):
        super().__init__(problem, num_ants, max_iterations)
        self.num_ants = num_ants
        self.alpha = alpha
        self.beta = beta
        self.evaporation_rate = evaporation_rate
        self.Q = Q
        
        self.num_dimensions = problem.num_dimensions
        self.pheromone = None
        self.heuristic = None
        self.run_time = 0

    def initialize(self):
        self.pheromone = np.ones((self.num_dimensions, self.num_dimensions)) * 0.1
        
        distances = self.problem.dataset.distances
        raw_heuristic = np.where(distances > 0, 1.0 / distances, 0)
        self.heuristic = raw_heuristic

    def _construct_solution(self) -> np.ndarray:
        start_node = 0
        unvisited = list(range(self.num_dimensions))
        unvisited.remove(start_node)
        
        path = [start_node]
        current = start_node
        
        while unvisited:
            probabilities = []
            for target in unvisited:
                tau = self.pheromone[current][target] ** self.alpha
                eta = self.heuristic[current][target] ** self.beta
                probabilities.append(tau * eta)
                
            sum_prob = sum(probabilities)
            if sum_prob == 0:
                probabilities = np.ones(len(unvisited)) / len(unvisited)
            else:
                probabilities = np.array(probabilities) / sum_prob
                
            next_node = np.random.choice(unvisited, p=probabilities)
            path.append(next_node)
            unvisited.remove(next_node)
            current = next_node
            
        return np.array(path)

    def _update_pheromones(self, ant_solutions: list, fitness_scores: np.ndarray):
        self.pheromone *= (1 - self.evaporation_rate)
        
        for i in range(len(ant_solutions)):
            path = ant_solutions[i]
            fitness = fitness_scores[i]
            
            deposit = self.Q * (fitness if fitness > 0 else 0.001)
            
            for j in range(len(path) - 1):
                from_node = path[j]
                to_node = path[j + 1]
                self.pheromone[from_node][to_node] += deposit

    def optimize(self, verbose: bool = True, print_interval: int = 10):
        start_time = time.time()
        self.initialize()
        
        for iteration in range(1, self.max_iterations + 1):
            ant_solutions = []
            fitness_scores = []
            
            for _ in range(self.num_ants):
                path = self._construct_solution()
                fitness = self.problem.evaluate(path)
                
                ant_solutions.append(path)
                fitness_scores.append(fitness)
                
            fitness_scores = np.array(fitness_scores)
            
            if self.problem.is_minimization:
                best_idx = np.argmin(fitness_scores)
            else:
                best_idx = np.argmax(fitness_scores)
                
            self.update_best_solution(ant_solutions[best_idx], fitness_scores[best_idx])
            self.convergence_curve.append(self.best_fitness)
            
            self._update_pheromones(ant_solutions, fitness_scores)
            
            if verbose and (iteration % print_interval == 0 or iteration == 1 or iteration == self.max_iterations):
                print(f"Iterasi [{iteration}/{self.max_iterations}] Fitness Terbaik: {self.best_fitness:.4f}")

        self.run_time = time.time() - start_time