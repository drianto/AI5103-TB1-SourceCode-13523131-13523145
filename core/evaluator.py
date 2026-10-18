def evaluate_solution(solution, dataset):
    vehicle_profits = []
    
    for veh_name, actions in solution.items():
        if not actions:
            vehicle_profits.append(0.0)
            continue
            
        veh_data = dataset.vehicles[veh_name]
        profit = 0.0
        current_time = 0.0
        total_distance = 0.0
        current_loc = veh_data['depot']
        used_implements = set()
        
        for action in actions:
            task_name = action['task']
            impl_name = action['implement']
            task_data = dataset.tasks[task_name]
            impl_data = dataset.implements[impl_name]
            
            # Cek Constraints
            if impl_name not in dataset.compat_veh_impl.get(veh_name, []) or \
               impl_name not in dataset.compat_task_impl.get(task_name, []):
                profit -= 99999
                
            # Cost alat & route ke depot alat
            if impl_name not in used_implements:
                profit -= impl_data['use_cost']
                used_implements.add(impl_name)
                
                dist_to_impl_depot = dataset.distances[current_loc][impl_data['depot']]
                total_distance += dist_to_impl_depot
                current_time += (dist_to_impl_depot / veh_data['speed'])
                profit -= (dist_to_impl_depot * veh_data['distance_cost'])
                current_loc = impl_data['depot']
                
            # Route ke ladang
            dist_to_task = dataset.distances[current_loc][task_name]
            total_distance += dist_to_task
            current_time += (dist_to_task / veh_data['speed'])
            profit -= (dist_to_task * veh_data['distance_cost'])
            
            if current_time < task_data['start_time']:
                current_time = task_data['start_time']
            elif current_time > task_data['end_time']:
                profit -= 1000 * (current_time - task_data['end_time'])
                
            # Eksekusi
            profit += task_data['revenue']
            current_time += task_data['service_time']
            current_loc = task_name

        # Going back & cek bensin
        dist_to_home = dataset.distances[current_loc][veh_data['depot']]
        total_distance += dist_to_home
        if total_distance > veh_data['max_distance']:
            profit -= 99999
            
        vehicle_profits.append(profit)
        
    worst_off_profit = min(vehicle_profits) if vehicle_profits else 0.0
    overall_profit = sum(vehicle_profits) if vehicle_profits else 0.0
    
    return worst_off_profit, overall_profit