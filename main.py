import os
import pandas as pd
import matplotlib.pyplot as plt

from core.afvrpi_problem import AFVRPIProblem
from algorithms.hill_climbing import HillClimbing
from algorithms.simulated_annealing import SimulatedAnnealing

def main():
    base_instances_dir = os.path.join("data", "instances")
    
    config = {
        "runs_per_exp": 5,      
        "hc_max_iter": 2000,
        "sa_init_temp": 10000.0,
        "sa_cooling": 0.99
    }
    
    print("="*60)
    print("MEMULAI EKSPERIMEN EVALUASI MASAL (BATCH PROCESSING)")
    print("="*60)
    
    raw_results = []
    contoh_history_hc = []
    contoh_history_sa = []
    contoh_sota_profit = 0
    contoh_nama_sampel = ""
    grafik_sudah_diambil = False

    if not os.path.exists(base_instances_dir):
        print(f"[FATAL ERROR] Folder {base_instances_dir} tidak ditemukan!")
        return

    config_folders = ["1D_5V_10I_30K", "1D_5V_10I_40K", "1D_5V_10I_50K"]
    
    for config_name in config_folders:
        config_dir = os.path.join(base_instances_dir, config_name)
        if not os.path.exists(config_dir):
            continue
            
        print(f"\n>>> Mulai Evaluasi Konfigurasi: {config_name}")
        exp_folders = [f for f in os.listdir(config_dir) if f.startswith('exp_') and os.path.isdir(os.path.join(config_dir, f))]
        exp_folders.sort(key=lambda x: int(x.split('_')[1])) 
        
        for exp_name in exp_folders:
            instance_dir = os.path.join(config_dir, exp_name)
            
            try:
                problem = AFVRPIProblem(instance_dir)
            except Exception as e:
                print(f"    [ERROR] Gagal memuat {instance_dir}. Detail: {e}")
                continue
                
            solutions_dir = os.path.join(instance_dir, 'solutions')
            sota_profit = 0
            if os.path.exists(solutions_dir):
                sota_files = [f for f in os.listdir(solutions_dir) if f.endswith('.json')]
                if sota_files:
                    sota_data = problem.dataset.load_baseline_solution(sota_files[0])
                    sota_profit = sota_data.get('objective_value', 0)
                    
                    if not grafik_sudah_diambil:
                        contoh_sota_profit = sota_profit

            for run in range(config["runs_per_exp"]):
                
                hc = HillClimbing(problem, max_iterations=config["hc_max_iter"])
                hc.optimize()
                hc_res = hc.get_results()
                
                raw_results.append({
                    "Config": config_name, "Dataset": exp_name, "Run": run + 1, "Algorithm": "Hill Climbing",
                    "SOTA_Worst_Off_Profit": sota_profit,
                    "Worst_Off_Profit": hc_res["best_fitness"],
                    "Overall_Profit": hc_res["overall_profit"], "Time_s": hc_res["run_time"]
                })
                
                if not grafik_sudah_diambil:
                    contoh_history_hc = hc_res["convergence_curve"]
                    contoh_nama_sampel = f"{config_name} {exp_name}"

                sa = SimulatedAnnealing(problem, initial_temp=config["sa_init_temp"], cooling_rate=config["sa_cooling"])
                sa.optimize()
                sa_res = sa.get_results()
                
                raw_results.append({
                    "Config": config_name, "Dataset": exp_name, "Run": run + 1, "Algorithm": "Simulated Annealing",
                    "SOTA_Worst_Off_Profit": sota_profit,
                    "Worst_Off_Profit": sa_res["best_fitness"],
                    "Overall_Profit": sa_res["overall_profit"], "Time_s": sa_res["run_time"]
                })
                
                if not grafik_sudah_diambil:
                    contoh_history_sa = sa_res["convergence_curve"]
                    grafik_sudah_diambil = True 
                    
            print(f"    [OK] Selesai: {exp_name}")

    print("\nMenyimpan hasil ke CSV...")
    df_results = pd.DataFrame(raw_results)
    df_results.to_csv("hasil_mentah_eksperimen.csv", index=False)
    print("[+] Berhasil menyimpan 'hasil_mentah_eksperimen.csv'")

    print("Menggambar Kurva Konvergensi >>")
    plt.figure(figsize=(10, 6))
    
    if contoh_sota_profit != 0:
        plt.axhline(y=contoh_sota_profit, color='r', linestyle='--', label=f'SOTA / DIMASA ({contoh_sota_profit})')
        
    plt.plot(contoh_history_hc, label='Hill Climbing', color='blue', alpha=0.7)
    plt.plot(contoh_history_sa, label='Simulated Annealing', color='green', alpha=0.7)
    
    plt.title(f'Kurva Konvergensi Algoritma Metaheuristik (Sampel {contoh_nama_sampel})')
    plt.xlabel('Iterasi')
    plt.ylabel('Worst-off Profit (Nilai Keadilan)')
    
    plt.legend()
    plt.grid(True)
    plt.savefig('kurva_konvergensi.png', dpi=300)
    print("[+] Berhasil menyimpan 'kurva_konvergensi.png'")

    print("Menggambar Boxplot >>")
    plt.figure(figsize=(10, 6))
    
    data_to_plot = [
        df_results['SOTA_Worst_Off_Profit'].unique(),
        df_results[df_results['Algorithm'] == 'Hill Climbing']['Worst_Off_Profit'],
        df_results[df_results['Algorithm'] == 'Simulated Annealing']['Worst_Off_Profit']
    ]
    
    plt.boxplot(data_to_plot)
    plt.xticks([1, 2, 3], ['SOTA (DIMASA)', 'Hill Climbing', 'Simulated Annealing'])
    plt.title('Distribusi Profit Keseluruhan (Semua Eksekusi)')
    plt.ylabel('Worst-off Profit')
    plt.grid(axis='y', linestyle='--', alpha=0.7)
    plt.savefig('boxplot_all_exp.png', dpi=300)
    print("[+] Berhasil menyimpan 'boxplot_all_exp.png'")

    print("\n" + "="*60)
    print("Rekapitulasi Hasil Rata-rata per Algoritma:")
    print("="*60)
    rekap = df_results.groupby("Algorithm")[["Worst_Off_Profit", "SOTA_Worst_Off_Profit", "Time_s"]].mean(numeric_only=True)
    print(rekap)

if __name__ == "__main__":
    main()