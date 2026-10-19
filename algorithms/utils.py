import random
import copy

def buat_solusi_awal(dataset):
    solusi = {veh: [] for veh in dataset.vehicles.keys()}
    daftar_tugas = list(dataset.tasks.keys())
    random.shuffle(daftar_tugas)
    
    daftar_traktor = list(dataset.vehicles.keys())
    
    for idx, tugas in enumerate(daftar_tugas):
        traktor = daftar_traktor[idx % len(daftar_traktor)]
        
        alat_cocok = list(
            set(dataset.compat_veh_impl.get(traktor, [])) & 
            set(dataset.compat_task_impl.get(tugas, []))
        )
        
        if len(alat_cocok) > 0:
            alat = random.choice(alat_cocok)
        else:
            alat = random.choice(list(dataset.implements.keys()))
            
        solusi[traktor].append({'task': tugas, 'implement': alat})
        
    return solusi

def get_neighbor(solusi_sekarang, dataset):
    tetangga = copy.deepcopy(solusi_sekarang)
    traktor_aktif = [v for v, rutelist in tetangga.items() if len(rutelist) > 0]
    
    if not traktor_aktif:
        return tetangga
        
    traktor_asal = random.choice(traktor_aktif)
    indeks_tugas = random.randrange(len(tetangga[traktor_asal]))
    aksi = tetangga[traktor_asal].pop(indeks_tugas)
    
    traktor_tujuan = random.choice(list(tetangga.keys()))
    
    # Cari utk traktor tujuan
    alat_cocok = list(
        set(dataset.compat_veh_impl.get(traktor_tujuan, [])) & 
        set(dataset.compat_task_impl.get(aksi['task'], []))
    )
    
    if len(alat_cocok) > 0:
        aksi['implement'] = random.choice(alat_cocok)
    else:
        # Jika tidak ada yang cocok sama sekali, kembalikan solusi tanpa ubah
        tetangga[traktor_asal].insert(indeks_tugas, aksi)
        return tetangga
        
    indeks_sisip = random.randint(0, len(tetangga[traktor_tujuan]))
    tetangga[traktor_tujuan].insert(indeks_sisip, aksi)
    
    return tetangga