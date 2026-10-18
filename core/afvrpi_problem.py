from core.base_problem import BaseProblem
from core.loader import AFVRPIDataset

class AFVRPIProblem(BaseProblem):
    def __init__(self, instance_path):
        super().__init__(num_dimensions=0, bounds=[], is_minimization=False)
        self.dataset = AFVRPIDataset(instance_path)
        self.last_overall_profit = 0.0
        self.last_penalty = 0.0
        
    def evaluate(self, solution) -> float:
        PENALTY_COMPATIBILITY = 999999.0
        PENALTY_CAPACITY = 999999.0
        PENALTY_AUTONOMY = 999999.0
        PENALTY_SHARED_IMPL = 999999.0
        PENALTY_TIME_MULTIPLIER = 1000.0

        vehicle_profits = []
        penalty = 0.0
        impl_owner = {}
        
        for veh_name, actions in solution.items():
            if not actions:
                vehicle_profits.append(0.0)
                continue
                
            veh_data = self.dataset.vehicles[veh_name]
            compat_veh = self.dataset.compat_veh_impl.get(veh_name, ())
            profit = 0.0
            current_time = 0.0
            total_distance = 0.0
            current_loc = veh_data['source_ref']
            
            current_impl = None
            capacity_used = {}
            used_implements = set()
            
            for action in actions:
                task_name = action['task']
                impl_name = action['implement']
                task_data = self.dataset.tasks[task_name]
                impl_data = self.dataset.implements[impl_name]
                
                if impl_name not in compat_veh or \
                   impl_name not in self.dataset.compat_task_impl.get(task_name, ()):
                    penalty += PENALTY_COMPATIBILITY
                    
                if impl_name != current_impl:
                    if current_impl is not None:
                        old_impl_data = self.dataset.implements[current_impl]
                        dist_to_drop = self.dataset.distances[current_loc][old_impl_data['sink_ref']]
                        total_distance += dist_to_drop
                        current_time += (dist_to_drop / veh_data['speed'])
                        profit -= (dist_to_drop * veh_data['distance_cost'])
                        current_loc = old_impl_data['sink_ref']
                    
                    dist_to_pickup = self.dataset.distances[current_loc][impl_data['source_ref']]
                    total_distance += dist_to_pickup
                    current_time += (dist_to_pickup / veh_data['speed'])
                    profit -= (dist_to_pickup * veh_data['distance_cost'])
                    current_loc = impl_data['source_ref']
                    
                    if impl_name not in used_implements:
                        profit -= impl_data['use_cost']
                        used_implements.add(impl_name)
                        # 1 alat hanya boleh dimiliki 1 traktor
                        if impl_owner.setdefault(impl_name, veh_name) != veh_name:
                            penalty += PENALTY_SHARED_IMPL
                    
                    current_impl = impl_name
                    
                # kapasitas kumulatif per alat (tidak reset saat diambil ulang)
                capacity_used[impl_name] = capacity_used.get(impl_name, 0.0) + task_data['demand']
                if capacity_used[impl_name] > impl_data['capacity']:
                    penalty += PENALTY_CAPACITY
                    
                dist_to_task = self.dataset.distances[current_loc][task_name]
                total_distance += dist_to_task
                current_time += (dist_to_task / veh_data['speed'])
                profit -= (dist_to_task * veh_data['distance_cost'])
                
                if current_time < task_data['start_time']:
                    current_time = task_data['start_time']
                elif current_time > task_data['end_time']:
                    penalty += PENALTY_TIME_MULTIPLIER * (current_time - task_data['end_time'])
                    
                profit += task_data['revenue']
                current_time += task_data['service_time']
                current_loc = task_name

            if current_impl is not None:
                last_impl_data = self.dataset.implements[current_impl]
                dist_to_drop = self.dataset.distances[current_loc][last_impl_data['sink_ref']]
                total_distance += dist_to_drop
                profit -= (dist_to_drop * veh_data['distance_cost'])
                current_loc = last_impl_data['sink_ref']

            dist_to_home = self.dataset.distances[current_loc][veh_data['sink_ref']]
            total_distance += dist_to_home
            profit -= (dist_to_home * veh_data['distance_cost'])
            
            if total_distance > veh_data['max_distance']:
                penalty += PENALTY_AUTONOMY
                
            vehicle_profits.append(profit)
            
        worst_off_profit = min(vehicle_profits) if vehicle_profits else 0.0
        self.last_overall_profit = sum(vehicle_profits) if vehicle_profits else 0.0
        self.last_penalty = penalty
        
        return worst_off_profit - penalty
        return worst_off_profit - penalty