from core.base_problem import BaseProblem
from core.loader import AFVRPIDataset
import math

class AFVRPIProblem(BaseProblem):
    def __init__(self, instance_path):
        super().__init__(num_dimensions=0, bounds=[], is_minimization=False)
        self.dataset = AFVRPIDataset(instance_path)
        self.last_overall_profit = 0.0
        
    def evaluate(self, solution) -> float:
        PENALTY_BASE = 5000.0
        PENALTY_TIME_MULTIPLIER = 100.0

        vehicle_profits = []
        global_used_implements = set()
        
        for veh_name, actions in solution.items():
            if not actions:
                vehicle_profits.append(0.0)
                continue
                
            veh_data = self.dataset.vehicles[veh_name]
            profit = 0.0
            current_time = 0.0
            total_distance = 0.0
            current_loc = veh_data['source_ref']
            
            current_impl = None
            current_capacity_used = 0.0
            used_implements_by_this_veh = set()
            
            for action in actions:
                task_name = action['task']
                impl_name = action['implement']
                task_data = self.dataset.tasks[task_name]
                impl_data = self.dataset.implements[impl_name]
                
                # Kompatibilitas
                if impl_name not in self.dataset.compat_veh_impl.get(veh_name, []) or \
                   impl_name not in self.dataset.compat_task_impl.get(task_name, []):
                    profit -= PENALTY_BASE
                    
                # Implement Swapping & Cek Penggunaan Ganda
                if impl_name != current_impl:
                    if impl_name in global_used_implements and impl_name not in used_implements_by_this_veh:
                        profit -= PENALTY_BASE
                        
                    if current_impl is not None:
                        old_impl_data = self.dataset.implements[current_impl]
                        dist_to_drop = math.floor(self.dataset.distances[current_loc][old_impl_data['sink_ref']])
                        total_distance += dist_to_drop
                        current_time += (dist_to_drop / veh_data['speed'])
                        profit -= (dist_to_drop * veh_data['distance_cost'])
                        current_loc = old_impl_data['sink_ref']
                    
                    dist_to_pickup = math.floor(self.dataset.distances[current_loc][impl_data['source_ref']])
                    total_distance += dist_to_pickup
                    current_time += (dist_to_pickup / veh_data['speed'])
                    profit -= (dist_to_pickup * veh_data['distance_cost'])
                    current_loc = impl_data['source_ref']
                    
                    if impl_name not in used_implements_by_this_veh:
                        profit -= impl_data['use_cost']
                        used_implements_by_this_veh.add(impl_name)
                        global_used_implements.add(impl_name)
                    
                    current_impl = impl_name
                    current_capacity_used = 0.0 
                    
                # Kapasitas Alat
                current_capacity_used += task_data['demand']
                if current_capacity_used > impl_data['capacity']:
                    overload = current_capacity_used - impl_data['capacity']
                    profit -= (PENALTY_BASE + overload * 500.0)
                    
                # Route & Time Windows
                dist_to_task = math.floor(self.dataset.distances[current_loc][task_name])
                total_distance += dist_to_task
                current_time += (dist_to_task / veh_data['speed'])
                profit -= (dist_to_task * veh_data['distance_cost'])
                
                if current_time < task_data['start_time']:
                    current_time = task_data['start_time'] # Menunggu
                elif current_time > task_data['end_time']:
                    keterlambatan = current_time - task_data['end_time']
                    profit -= PENALTY_TIME_MULTIPLIER * keterlambatan
                    
                profit += task_data['revenue']
                current_time += task_data['service_time']
                current_loc = task_name

            # Route Pulang
            if current_impl is not None:
                last_impl_data = self.dataset.implements[current_impl]
                dist_to_drop = math.floor(self.dataset.distances[current_loc][last_impl_data['sink_ref']])
                total_distance += dist_to_drop
                profit -= (dist_to_drop * veh_data['distance_cost'])
                current_loc = last_impl_data['sink_ref']

            dist_to_home = math.floor(self.dataset.distances[current_loc][veh_data['sink_ref']])
            total_distance += dist_to_home
            profit -= (dist_to_home * veh_data['distance_cost'])
            
            # Batre & Bensin
            if total_distance > veh_data['max_distance']:
                excess_dist = total_distance - veh_data['max_distance']
                profit -= (PENALTY_BASE + excess_dist * 100.0)
                
            vehicle_profits.append(profit)
            
        worst_off_profit = min(vehicle_profits) if vehicle_profits else 0.0
        self.last_overall_profit = sum(vehicle_profits) if vehicle_profits else 0.0
        
        return worst_off_profit