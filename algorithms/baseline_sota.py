import json
import os

def run_sota_baseline(dataset, json_filename):
    filepath = os.path.join(dataset.instance_path, 'solutions', json_filename)
    
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"File baseline solution {json_filename} tidak ditemukan di {filepath}")
        
    with open(filepath, 'r') as f:
        data = json.load(f)
        
    return {
        "algorithm": data.get("algorithm", "DIMASA (Paper)"),
        "worst_off_profit": data.get("objective_value", 0.0),
        "overall_profit": data.get("overall_profit", 0.0),
        "run_time": data.get("run_time", 0.0)
    }