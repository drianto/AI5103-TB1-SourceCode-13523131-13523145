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

        # Parse Depots
        for _, row in df_depots.iterrows():
            self.depots[row['name']] = {
                'x': float(row['x']), 
                'y': float(row['y'])
            }

        # Parse Tasks
        for _, row in df_tasks.iterrows():
            self.tasks[row['name']] = {
                'x': float(row['x']), 
                'y': float(row['y']),
                'start_time': float(row['start_time']), 
                'end_time': float(row['end_time']),
                'service_time': float(row['service_time']), 
                'demand': float(row['demand']),
                'revenue': float(row['revenue'])
            }

        # Parse Vehicles
        for _, row in df_vehicles.iterrows():
            self.vehicles[row['name']] = {
                'max_distance': float(row['max_distance']),
                'speed': float(row['speed']),
                'distance_cost': float(row['distance_cost']),
                'source_ref': row['source_ref'],
                'sink_ref': row['sink_ref']
            }

        # Parse Implements
        for _, row in df_implements.iterrows():
            self.implements[row['name']] = {
                'capacity': float(row['capacity']),
                'use_cost': float(row['use_cost']),
                'source_ref': row['source_ref'],
                'sink_ref': row['sink_ref']
            }

        # Parse Compatibilities
        for _, row in df_cti.iterrows():
            task_name = row['name']
            compatible = [col for col in df_cti.columns if col != 'name' and row[col] == 1.0]
            self.compat_task_impl[task_name] = compatible

        for _, row in df_cvi.iterrows():
            veh_name = row['name']
            compatible = [col for col in df_cvi.columns if col != 'name' and row[col] == 1.0]
            self.compat_veh_impl[veh_name] = compatible

        # Precompute Distances
        all_nodes = {**self.tasks, **self.depots}
        for node1_name, node1_data in all_nodes.items():
            self.distances[node1_name] = {}
            for node2_name, node2_data in all_nodes.items():
                if node1_name == node2_name:
                    self.distances[node1_name][node2_name] = 0.0
                else:
                    dist = math.sqrt((node1_data['x'] - node2_data['x'])**2 + (node1_data['y'] - node2_data['y'])**2)
                    self.distances[node1_name][node2_name] = dist

    def load_baseline_solution(self, json_filename):
        solution_file = os.path.join(self.instance_path, 'solutions', json_filename)
        if not os.path.exists(solution_file):
            print(f"Warning: File solusi {json_filename} tidak ditemukan.")
            return None
        with open(solution_file, 'r') as f:
            data = json.load(f)
        return data