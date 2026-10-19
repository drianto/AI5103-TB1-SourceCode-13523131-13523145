# core/evaluator.py

def evaluate_solution(solution, dataset):
    # Hard Constraints
    PENALTY_COMPATIBILITY = 999999.0
    PENALTY_CAPACITY = 999999.0
    PENALTY_AUTONOMY = 999999.0
    PENALTY_TIME_MULTIPLIER = 1000.0

    vehicle_profits = []
    
    for veh_name, actions in solution.items():
        # Traktor tidak diberikan tugas, then profit = 0
        if not actions:
            vehicle_profits.append(0.0)
            continue
            
        veh_data = dataset.vehicles[veh_name]
        
        profit = 0.0
        current_time = 0.0
        total_distance = 0.0
        
        current_loc = veh_data['source_ref']
        
        current_impl = None
        current_capacity_used = 0.0
        used_implements = set()
        
        for action in actions:
            task_name = action['task']
            impl_name = action['implement']
            
            task_data = dataset.tasks[task_name]
            impl_data = dataset.implements[impl_name]
            
            if impl_name not in dataset.compat_veh_impl.get(veh_name, []):
                profit -= PENALTY_COMPATIBILITY
            if impl_name not in dataset.compat_task_impl.get(task_name, []):
                profit -= PENALTY_COMPATIBILITY
                
            # Implement Swapping: Jika alat yang dibawa traktor berbeda dengan alat yang dibutuhkan untuk tugas current, maka traktor harus swap alatnya.
            if impl_name != current_impl:
                # If lagi bawa alat, kembalikan ke sink_ref alatnya
                if current_impl is not None:
                    old_impl_data = dataset.implements[current_impl]
                    dist_to_drop = dataset.distances[current_loc][old_impl_data['sink_ref']]
                    
                    total_distance += dist_to_drop
                    current_time += (dist_to_drop / veh_data['speed'])
                    profit -= (dist_to_drop * veh_data['distance_cost'])
                    current_loc = old_impl_data['sink_ref']
                
                # Pergi ke depo alat baru
                dist_to_pickup = dataset.distances[current_loc][impl_data['source_ref']]
                total_distance += dist_to_pickup
                current_time += (dist_to_pickup / veh_data['speed'])
                profit -= (dist_to_pickup * veh_data['distance_cost'])
                current_loc = impl_data['source_ref']
                
                # Bayar biaya sewa alat (bayar 1x saat pertama kali dipakai traktor ini)
                if impl_name not in used_implements:
                    profit -= impl_data['use_cost']
                    used_implements.add(impl_name)
                
                current_impl = impl_name
                current_capacity_used = 0.0 
                
            # Kaasitas Alat: Jika kapasitas alat over, maka penalti
            current_capacity_used += task_data['demand']
            if current_capacity_used > impl_data['capacity']:
                profit -= PENALTY_CAPACITY
                
            # Route ke ladang & Time Windows: Jika traktor datang lebih awal, then tunggu. Jika terlambat, maka penalti
            dist_to_task = dataset.distances[current_loc][task_name]
            total_distance += dist_to_task
            current_time += (dist_to_task / veh_data['speed'])
            profit -= (dist_to_task * veh_data['distance_cost'])
            
            # Time Windows
            if current_time < task_data['start_time']:
                # Datang lebih awal -> Traktor harus menunggu hingga start_time
                current_time = task_data['start_time']
            elif current_time > task_data['end_time']:
                # Datang terlambat -> Kena penalti
                profit -= PENALTY_TIME_MULTIPLIER * (current_time - task_data['end_time'])
                
            profit += task_data['revenue']
            current_time += task_data['service_time']
            current_loc = task_name

        # Route ke depo alat terakhir
        if current_impl is not None:
            last_impl_data = dataset.implements[current_impl]
            dist_to_drop = dataset.distances[current_loc][last_impl_data['sink_ref']]
            
            total_distance += dist_to_drop
            profit -= (dist_to_drop * veh_data['distance_cost'])
            current_loc = last_impl_data['sink_ref']

        # Route pulang ke sink_ref traktor
        dist_to_home = dataset.distances[current_loc][veh_data['sink_ref']]
        total_distance += dist_to_home
        profit -= (dist_to_home * veh_data['distance_cost'])
        
        # Cek Autonomy: Jika total jarak > max_distance, then penalti
        if total_distance > veh_data['max_distance']:
            profit -= PENALTY_AUTONOMY
            
        vehicle_profits.append(profit)
        
    # Hitung Worst-off Profit dan Overall Profit
    worst_off_profit = min(vehicle_profits) if vehicle_profits else 0.0
    overall_profit = sum(vehicle_profits) if vehicle_profits else 0.0
    
    return worst_off_profit, overall_profit