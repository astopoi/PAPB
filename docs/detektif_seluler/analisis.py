"""Jalankan alat praktikum asli; simpan log dan grafik tanpa mengubah referensi."""
from pathlib import Path
import subprocess
import os
from concurrent.futures import ThreadPoolExecutor

ROOT = Path('/home/astopoi/Downloads/untuk_mahasiswa/praktikum_seluler')
OUT = Path(__file__).resolve().parent / 'hasil'
PYTHON = '/tmp/detektif-venv/bin/python'
CONFIG = [(1,20e6,2329.8),(2,20e6,2050),(3,20e6,1870),(4,4e6,1859.6),(5,15.36e6,945.2)]
def run(item):
    n, fs, fc = item
    prefix = OUT / f'misteri_{n}'
    inp = ROOT / 'data/misteri' / f'misteri_{n}.cs8'
    jobs = [('bentuk_sinyal.py','bentuk')]
    if n in (1,2,3,5): jobs.append(('cari_sel_lte.py','lte'))
    if n == 4: jobs.append(('gsm_fcch.py','gsm'))
    env = dict(os.environ, MPLCONFIGDIR='/tmp/detektif-mpl', OPENBLAS_NUM_THREADS='1', OMP_NUM_THREADS='1')
    for script, tag in jobs:
        cmd = [PYTHON,str(ROOT/script),str(inp),'--fs',str(fs),'--fc',str(fc),'--out',str(prefix)]
        with open(str(prefix)+'_'+tag+'.log','w') as log:
            result = subprocess.run(cmd,stdout=log,stderr=subprocess.STDOUT,env=env)
        print(n,tag,result.returncode,flush=True)
    if n == 3:
        cmd = [PYTHON,str(ROOT/'cari_sel_lte.py'),str(inp),'--fs',str(fs),'--fc',str(fc),
               '--ambang','0.1','--out',str(prefix)+'_sensitif']
        with open(str(prefix)+'_sensitif_lte.log','w') as log:
            result = subprocess.run(cmd,stdout=log,stderr=subprocess.STDOUT,env=env)
        print(n,'lte sensitif',result.returncode,flush=True)
if __name__ == '__main__':
    OUT.mkdir(exist_ok=True)
    with ThreadPoolExecutor(max_workers=2) as pool:
        list(pool.map(run, CONFIG))
