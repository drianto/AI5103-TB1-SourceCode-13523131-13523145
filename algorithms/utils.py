import random
from bisect import bisect_left, bisect_right

def _pemilik_alat(solusi):
    pemilik = {}
    for veh, rute in solusi.items():
        for aksi in rute:
            pemilik.setdefault(aksi['implement'], set()).add(veh)
    return pemilik

def _posisi_sisip(rute, tugas, dataset):
    # sisip sesuai urutan start_time agar time window terjaga
    starts = [dataset.tasks[a['task']]['start_time'] for a in rute]
    s = dataset.tasks[tugas]['start_time']
    return random.randint(bisect_left(starts, s), bisect_right(starts, s))

def _pilih_alat(traktor, tugas, rute, pemilik, dataset):
    demand = dataset.tasks[tugas]['demand']
    kandidat = []
    for alat in dataset.compat_veh_impl.get(traktor, set()) & dataset.compat_task_impl.get(tugas, set()):
        if pemilik.get(alat, set()) - {traktor}:
            continue
        terpakai = sum(dataset.tasks[a['task']]['demand'] for a in rute if a['implement'] == alat)
        if terpakai + demand <= dataset.implements[alat]['capacity']:
            kandidat.append(alat)
    if not kandidat:
        return None
    milik_sendiri = [a for a in kandidat if traktor in pemilik.get(a, ())]
    return random.choice(milik_sendiri or kandidat)

def buat_solusi_awal(dataset):
    solusi = {veh: [] for veh in dataset.vehicles}
    daftar_tugas = list(dataset.tasks.keys())
    random.shuffle(daftar_tugas)
    pemilik = {}
    
    for tugas in daftar_tugas:
        urutan_traktor = sorted(dataset.vehicles, key=lambda v: (len(solusi[v]), random.random()))
        traktor, alat = None, None
        for v in urutan_traktor:
            alat = _pilih_alat(v, tugas, solusi[v], pemilik, dataset)
            if alat is not None:
                traktor = v
                break
        
        if traktor is None:
            traktor = random.choice(list(dataset.vehicles.keys()))
            alat_cocok = list(
                set(dataset.compat_veh_impl.get(traktor, [])) & 
                set(dataset.compat_task_impl.get(tugas, []))
            )
            alat = random.choice(alat_cocok) if alat_cocok else random.choice(list(dataset.implements.keys()))
        
        pemilik.setdefault(alat, set()).add(traktor)
        solusi[traktor].insert(_posisi_sisip(solusi[traktor], tugas, dataset), {'task': tugas, 'implement': alat})
    return solusi

def _relokasi(solusi, dataset):
    traktor_aktif = [v for v, rute in solusi.items() if rute]
    if not traktor_aktif:
        return None
    traktor_asal = random.choice(traktor_aktif)
    traktor_tujuan = random.choice(list(solusi.keys()))
    
    tetangga = dict(solusi)
    tetangga[traktor_asal] = list(solusi[traktor_asal])
    aksi = tetangga[traktor_asal].pop(random.randrange(len(tetangga[traktor_asal])))
    if traktor_tujuan != traktor_asal:
        tetangga[traktor_tujuan] = list(solusi[traktor_tujuan])
    
    alat = _pilih_alat(traktor_tujuan, aksi['task'], tetangga[traktor_tujuan], _pemilik_alat(tetangga), dataset)
    if alat is None:
        return None
    
    rute = tetangga[traktor_tujuan]
    rute.insert(_posisi_sisip(rute, aksi['task'], dataset), {'task': aksi['task'], 'implement': alat})
    return tetangga

def _tukar(solusi, dataset):
    traktor_aktif = [v for v, rute in solusi.items() if rute]
    if len(traktor_aktif) < 2:
        return None
    va, vb = random.sample(traktor_aktif, 2)
    
    tetangga = dict(solusi)
    tetangga[va] = list(solusi[va])
    tetangga[vb] = list(solusi[vb])
    aksi_a = tetangga[va].pop(random.randrange(len(tetangga[va])))
    aksi_b = tetangga[vb].pop(random.randrange(len(tetangga[vb])))
    
    pemilik = _pemilik_alat(tetangga)
    alat_a = _pilih_alat(vb, aksi_a['task'], tetangga[vb], pemilik, dataset)
    alat_b = _pilih_alat(va, aksi_b['task'], tetangga[va], pemilik, dataset)
    if alat_a is None or alat_b is None or alat_a == alat_b:
        return None
    
    tetangga[vb].insert(_posisi_sisip(tetangga[vb], aksi_a['task'], dataset), {'task': aksi_a['task'], 'implement': alat_a})
    tetangga[va].insert(_posisi_sisip(tetangga[va], aksi_b['task'], dataset), {'task': aksi_b['task'], 'implement': alat_b})
    return tetangga

def dapatkan_tetangga(solusi_sekarang, dataset, max_percobaan=20):
    # tanpa deepcopy: hanya rute yang berubah yang disalin
    for _ in range(max_percobaan):
        gerakan = _relokasi if random.random() < 0.6 else _tukar
        tetangga = gerakan(solusi_sekarang, dataset)
        if tetangga is not None:
            return tetangga
    return solusi_sekarang

def dapatkan_tetangga(solusi_sekarang, dataset, max_percobaan=20):
    # tanpa deepcopy: hanya rute yang berubah yang disalin
    for _ in range(max_percobaan):
        gerakan = _relokasi if random.random() < 0.6 else _tukar
        tetangga = gerakan(solusi_sekarang, dataset)
        if tetangga is not None:
            return tetangga
    return solusi_sekarang
    return tetangga