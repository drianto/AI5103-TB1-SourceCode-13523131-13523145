# AFVRPI Metaheuristic Problem Solving Agent

Repositori ini berisi implementasi *Problem Solving Agent* untuk menyelesaikan persoalan **Agricultural Fleet Vehicle Routing Problem with Implements (AFVRPI)**. Proyek ini membandingkan algoritma *Local Search* (Hill Climbing, Simulated Annealing) dengan *Metaheuristik* (Genetic Algorithm, Ant Colony Optimization) terhadap nilai SOTA dari Gurobi.

## Struktur Direktori
- `data/instances/` : Berisi dataset *benchmark* AFVRPI dan solusi SOTA referensi.
- `core/` : Modul pemrosesan (`loader.py`), arsitektur OOP dasar (`base_problem.py`, `base_algorithm.py`), dan evaluator AFVRPI (`afvrpi_problem.py`).
- `algorithms/` : Implementasi algoritma metaheuristik dan fungsi pergerakan tetangga (`utils.py`).
- `main.py` : Orkestrator utama untuk *batch processing* dan visualisasi eksperimen.

## Cara Instalasi (Prerequisites)
Pastikan Anda menggunakan **Python 3.8+**. Lakukan instalasi pustaka yang dibutuhkan menggunakan perintah berikut di terminal:

```bash
pip install -r requirements.txt
```

## Cara Menjalankan & Mereproduksi Hasil (Reproducibility)
Jalankan perintah berikut di *root* direktori:

```bash
python main.py
```

### Output yang Dihasilkan
Setelah perintah di atas selesai dieksekusi, program akan secara otomatis menghasilkan *deliverables* berikut di dalam folder utama:
1. `hasil_mentah_eksperimen.csv` : Log data dari setiap *run* per algoritma untuk uji statistik.
2. `kurva_konvergensi.png` : Grafik kurva konvergensi dari 4 algoritma yang diuji (dibuat dengan Matplotlib).
3. `boxplot_all_exp.png` : Visualisasi distribusi *Worst-off Profit* keseluruhan algoritma.
4. `jadwal_terbaik/` : Folder berisi jadwal harian traktor dalam format `.json` dari solusi terbaik tiap algoritma.
5. **Terminal Output** : Tabel rekapitulasi statistik formal (Best, Mean, Std, Worst, Mean Time, dan Gap % terhadap SOTA).
