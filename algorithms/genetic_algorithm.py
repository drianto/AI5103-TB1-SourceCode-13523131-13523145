import time
import copy
import random
import numpy as np
from core.base_algorithm import BaseAlgorithm
from core.base_problem import BaseProblem
from algorithms.utils import buat_solusi_awal, get_neighbor

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

    def _crossover(self, parent1, parent2):
        # Route-Preserving Crossover 
        if random.random() > self.crossover_rate:
            return copy.deepcopy(parent1)
            
        child = {veh: [] for veh in self.problem.dataset.vehicles}
        
        # Warisin route utuh (satu traktor random from Parent 1)
        veh_to_keep = random.choice(list(child.keys()))
        child[veh_to_keep] = copy.deepcopy(parent1[veh_to_keep])
        
        assigned_tasks = {action['task'] for action in child[veh_to_keep]}
        
        # Warisin sisa task from Parent 2
        for veh, actions in parent2.items():
            if veh == veh_to_keep: continue
            for action in actions:
                if action['task'] not in assigned_tasks:
                    child[veh].append(copy.deepcopy(action))
                    assigned_tasks.add(action['task'])
                    
        # If ada tugas yang ketinggal (eg. karna perbedaan komposisi) = force
        all_tasks = set(self.problem.dataset.tasks.keys())
        missing_tasks = all_tasks - assigned_tasks
        for task in missing_tasks:
            valid_veh = random.choice(list(child.keys()))
            alat_cocok = list(set(self.problem.dataset.compat_veh_impl.get(valid_veh, [])) & 
                              set(self.problem.dataset.compat_task_impl.get(task, [])))
            alat = random.choice(alat_cocok) if alat_cocok else random.choice(list(self.problem.dataset.implements.keys()))
            child[valid_veh].append({'task': task, 'implement': alat})
            
        return child

    def optimize(self):
        start_time = time.time()
        self.initialize()
        
        for generation in range(1, self.max_iterations + 1):
            self._evaluate_population()
            
            best_idx = np.argmax(self.fitness_scores)
            self.update_best_solution(self.population[best_idx], self.fitness_scores[best_idx])
            self.convergence_curve.append(self.best_fitness)

            new_population = [copy.deepcopy(self.best_solution)]
            
            while len(new_population) < self.population_size:
                idx1, idx2 = np.random.choice(self.population_size, 2, replace=False)
                p1 = self.population[idx1] if self.fitness_scores[idx1] > self.fitness_scores[idx2] else self.population[idx2]
                
                idx3, idx4 = np.random.choice(self.population_size, 2, replace=False)
                p2 = self.population[idx3] if self.fitness_scores[idx3] > self.fitness_scores[idx4] else self.population[idx4]

                child = self._crossover(p1, p2)

                if np.random.rand() < self.mutation_rate:
                    child = get_neighbor(child, self.problem.dataset)
                    
                new_population.append(child)
                    
            self.population = new_population
            
        self.run_time = time.time() - start_time

    def get_results(self) -> dict:
        results = super().get_results()
        results["run_time"] = self.run_time
        self.problem.evaluate(self.best_solution)
        results["overall_profit"] = self.problem.last_overall_profit
        return results