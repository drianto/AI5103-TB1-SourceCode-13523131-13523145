import time
import random
import numpy as np
from core.base_algorithm import BaseAlgorithm
from core.base_problem import BaseProblem

class AntColonyOptimization(BaseAlgorithm):
    def __init__(self, problem: BaseProblem, num_ants: int = 10, max_iterations: int = 50,
                 alpha: float = 1.0, beta: float = 2.0, evaporation_rate: float = 0.1, Q: float = 100):
        super().__init__(problem, population_size=num_ants, max_iterations=max_iterations)
        self.num_ants = num_ants
        self.alpha = alpha
        self.beta = beta
        self.evaporation_rate = evaporation_rate
        self.Q = Q
        
        self.vehicles = []
        self.tasks = []
        self.pheromone = None
        self.run_time = 0.0

    def initialize(self):
        self.vehicles = list(self.problem.dataset.vehicles.keys())
        self.tasks = list(self.problem.dataset.tasks.keys())
        self.pheromone = np.ones((len(self.vehicles), len(self.tasks))) * 0.1

    def _construct_solution(self):
        dataset = self.problem.dataset
        solution = {v: [] for v in self.vehicles}
        
        unassigned_tasks = list(self.tasks)
        
        unassigned_tasks.sort(key=lambda t: dataset.tasks[t]['start_time'])
        
        for task in unassigned_tasks:
            t_idx = self.tasks.index(task)
            probabilities = []
            
            for v_idx, veh in enumerate(self.vehicles):
                tau = self.pheromone[v_idx][t_idx] ** self.alpha
                
                # Heuristik: Utamakan traktor yang alatnya cocok dengan tugas ini
                alat_cocok = list(set(dataset.compat_veh_impl.get(veh, [])) & set(dataset.compat_task_impl.get(task, [])))
                eta = 2.0 if len(alat_cocok) > 0 else 0.1 # Penalti probabilitas jika alat tidak cocok
                
                probabilities.append(tau * (eta ** self.beta))
                
            sum_prob = sum(probabilities)
            probs = np.ones(len(self.vehicles)) / len(self.vehicles) if sum_prob == 0 else np.array(probabilities) / sum_prob
                
            chosen_v_idx = np.random.choice(len(self.vehicles), p=probs)
            chosen_veh = self.vehicles[chosen_v_idx]
            
            alat_cocok = list(set(dataset.compat_veh_impl.get(chosen_veh, [])) & set(dataset.compat_task_impl.get(task, [])))
            alat = random.choice(alat_cocok) if alat_cocok else random.choice(list(dataset.implements.keys()))
            
            solution[chosen_veh].append({'task': task, 'implement': alat})
            
        return solution

    def optimize(self):
        start_time = time.time()
        self.initialize()
        
        best_sol_in_run = None
        best_fit_in_run = float('-inf')
        
        for iteration in range(1, self.max_iterations + 1):
            ant_solutions = []
            fitness_scores = []
            
            for _ in range(self.num_ants):
                sol = self._construct_solution()
                fit = self.problem.evaluate(sol)
                ant_solutions.append(sol)
                fitness_scores.append(fit)
                
            fitness_scores = np.array(fitness_scores)
            best_idx = np.argmax(fitness_scores)
            
            if fitness_scores[best_idx] > best_fit_in_run:
                best_fit_in_run = fitness_scores[best_idx]
                best_sol_in_run = ant_solutions[best_idx]
                
            self.update_best_solution(best_sol_in_run, best_fit_in_run)
            self.convergence_curve.append(self.best_fitness)
            
            self.pheromone *= (1 - self.evaporation_rate)
            for idx, sol in enumerate(ant_solutions):
                fit = fitness_scores[idx]
                reinforcement = self.Q / (abs(fit) + 1.0) 
                for veh, actions in sol.items():
                    v_idx = self.vehicles.index(veh)
                    for action in actions:
                        t_idx = self.tasks.index(action['task'])
                        self.pheromone[v_idx][t_idx] += reinforcement
                            
        self.run_time = time.time() - start_time

    def get_results(self) -> dict:
        results = super().get_results()
        results["run_time"] = self.run_time
        self.problem.evaluate(self.best_solution)
        results["overall_profit"] = self.problem.last_overall_profit
        return results