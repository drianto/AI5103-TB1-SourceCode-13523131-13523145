import time
import numpy as np
from core.base_algorithm import BaseAlgorithm
from core.base_problem import BaseProblem

class GeneticAlgorithm(BaseAlgorithm):
    def __init__(self, problem: BaseProblem, population_size: int, max_iterations: int, 
                 crossover_rate: float = 0.8, mutation_rate: float = 0.05):
        super().__init__(problem, population_size, max_iterations)
        self.crossover_rate = crossover_rate
        self.mutation_rate = mutation_rate
        self.population = None
        self.fitness_scores = None
        self.run_time = 0.0

    def initialize(self):
        lows = [b[0] for b in self.problem.bounds]
        highs = [b[1] for b in self.problem.bounds]
        self.population = np.random.uniform(
            low=lows, 
            high=highs, 
            size=(self.population_size, self.problem.num_dimensions)
        )

    def _evaluate_population(self):
        self.fitness_scores = np.array([self.problem.evaluate(ind) for ind in self.population])

    def _roulette_wheel_selection(self) -> np.ndarray:
        fits = self.fitness_scores.copy()
        min_fit = np.min(fits)
        if min_fit < 0:
            fits = fits - min_fit + 1e-6

        total_fitness = np.sum(fits)
        if total_fitness == 0:
            probabilities = np.ones(self.population_size) / self.population_size
        else:
            probabilities = fits / total_fitness

        selected_idx = np.random.choice(self.population_size, p=probabilities)
        return self.population[selected_idx].copy()

    def _crossover(self, parent1: np.ndarray, parent2: np.ndarray):
        if np.random.rand() < self.crossover_rate:
            point = np.random.randint(1, self.problem.num_dimensions)
            child1 = np.concatenate([parent1[:point], parent2[point:]])
            child2 = np.concatenate([parent2[:point], parent1[point:]])
            return child1, child2
        return parent1.copy(), parent2.copy()

    def _mutate(self, child: np.ndarray) -> np.ndarray:
        for i in range(self.problem.num_dimensions):
            if np.random.rand() < self.mutation_rate:
                low, high = self.problem.bounds[i]
                child[i] = np.random.uniform(low, high)
        return child

    def optimize(self, verbose: bool = True, print_interval: int = 10):
        start_time = time.time()
        self.initialize()
        
        for generation in range(1, self.max_iterations + 1):
            self._evaluate_population()
            
            if self.problem.is_minimization:
                best_idx = np.argmin(self.fitness_scores)
            else:
                best_idx = np.argmax(self.fitness_scores)
                
            self.update_best_solution(self.population[best_idx], self.fitness_scores[best_idx])
            self.convergence_curve.append(self.best_fitness)
            
            if verbose and (generation % print_interval == 0 or generation == 1 or generation == self.max_iterations):
                print(f"Generasi [{generation}/{self.max_iterations}] Fitness Terbaik: {self.best_fitness:.4f}")

            new_population = [self.best_solution.copy()]
            
            while len(new_population) < self.population_size:
                parent1 = self._roulette_wheel_selection()
                parent2 = self._roulette_wheel_selection()
                child1, child2 = self._crossover(parent1, parent2)
                child1 = self._mutate(child1)
                child2 = self._mutate(child2)
                
                new_population.append(child1)
                if len(new_population) < self.population_size:
                    new_population.append(child2)
                    
            self.population = np.array(new_population)
            
        self.run_time = time.time() - start_time