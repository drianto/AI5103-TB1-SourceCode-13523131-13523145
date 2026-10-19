import pandas as pd
import os
import json
import math

class AFVRPIDataset:
    def __init__(self, instance_path):
        self.instance_path = instance_path
        self.tasks = {}
        self.vehicles = {}
        self.implements = {}
        self.depots = {}
        self.compat_task_impl = {}
        self.compat_veh_impl = {}
        self.distances = {}
        self.load_data()

    def load_data(self):
        df_tasks = pd.read_csv(os.path.join(self.instance_path, 'tasks.csv'))
        df_vehicles = pd.read_csv(os.path.join(self.instance_path, 'vehicles.csv'))
        df_implements = pd.read_csv(os.path.join(self.instance_path, 'implements.csv'))
        df_cti = pd.read_csv(os.path.join(self.instance_path, 'compatibilities_tasks_implements.csv'))
        df_cvi = pd.read_csv(os.path.join(self.instance_path, 'compatibilities_vehicles_implements.csv'))
        df_depots = pd.read_csv(os.path.join(self.instance_path, 'depots.csv'))

        for _, row in df_depots.iterrows():
            self.depots[row['name']] = {'x': float(row['x']), 'y': float(row['y'])}

        for _, row in df_tasks.iterrows():
            self.tasks[row['name']] = {
                'x': float(row['x']), 'y': float(row['y']),
                'start_time': float(row['start_time']), 'end_time': float(row['end_time']),
                'service_time': float(row['service_time']), 'demand': float(row['demand']),
                'revenue': float(row['revenue'])
            }

        for _, row in df_vehicles.iterrows():
            self.vehicles[row['name']] = {
                'max_distance': float(row['max_distance']),
                'speed': float(row['speed']),
                'distance_cost': float(row['distance_cost']),
                'source_ref': row['source_ref'],
                'sink_ref': row['sink_ref']
            }

        for _, row in df_implements.iterrows():
            self.implements[row['name']] = {
                'capacity': float(row['capacity']),
                'use_cost': float(row['use_cost']),
                'source_ref': row['source_ref'],
                'sink_ref': row['sink_ref']
            }

        for _, row in df_cti.iterrows():
            self.compat_task_impl[row['name']] = {col for col in df_cti.columns if col != 'name' and row[col] == 1.0}

        for _, row in df_cvi.iterrows():
            self.compat_veh_impl[row['name']] = {col for col in df_cvi.columns if col != 'name' and row[col] == 1.0}

        # Prekomputasi Jarak Euclid 
        all_nodes = {**self.tasks, **self.depots}
        for node1, data1 in all_nodes.items():
            self.distances[node1] = {}
            for node2, data2 in all_nodes.items():
                if node1 == node2:
                    self.distances[node1][node2] = 0.0
                else:
                    # floor: sesuai jarak integer SOTA
                    self.distances[node1][node2] = float(math.floor(math.sqrt((data1['x'] - data2['x'])**2 + (data1['y'] - data2['y'])**2)))

    def load_baseline_solution(self, json_filename):
        solution_file = os.path.join(self.instance_path, 'solutions', json_filename)
        if not os.path.exists(solution_file):
            return None
        with open(solution_file, 'r') as f:
            data = json.load(f)
        return data