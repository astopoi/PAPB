"""Pengujian UI lokasi pada HP fisik; tidak memasang mock location."""
from pathlib import Path
import json
import re
import subprocess
import sys
import time
import xml.etree.ElementTree as E

OUT = Path(__file__).resolve().parent
SH = OUT / 'screenshots'
PKG = 'com.example.bab6'

def adb(*args):
    return subprocess.check_output(['adb', *args], stderr=subprocess.STDOUT)

def dump():
    for _ in range(4):
        adb('shell', 'uiautomator', 'dump', '/sdcard/bab10.xml')
        xml = adb('exec-out', 'cat', '/sdcard/bab10.xml')
        if xml.startswith(b'<?xml'):
            (OUT/'ui-terakhir.xml').write_bytes(xml)
            return E.fromstring(xml)
        time.sleep(.5)
    raise RuntimeError('Tidak dapat membaca hierarki UI')

def labels(root):
    return [n.get('text') for n in root.iter('node') if n.get('text')]

def wait(predicate, seconds=25):
    deadline = time.monotonic() + seconds
    while time.monotonic() < deadline:
        r = dump()
        if predicate(r): return r
        time.sleep(.3)
    raise AssertionError(labels(r))

def wait_text(text): return wait(lambda r: text in labels(r))

def tap_node(n):
    x1,y1,x2,y2 = map(int,re.findall(r'\d+',n.get('bounds')))
    adb('shell','input','tap',str((x1+x2)//2),str((y1+y2)//2))
    time.sleep(.6)

def tap(text):
    r = wait_text(text)
    tap_node(next(n for n in r.iter('node') if n.get('text') == text))

def tap_id(suffix):
    r = wait(lambda r: any(n.get('resource-id','').endswith(suffix) for n in r.iter('node')))
    tap_node(next(n for n in r.iter('node') if n.get('resource-id','').endswith(suffix)))

def shot(name):
    time.sleep(.5)
    data = adb('exec-out','screencap','-p')
    assert data.startswith(b'\x89PNG')
    (SH/name).write_bytes(data)
    print('Screenshot:',name,flush=True)

def back():
    adb('shell','input','keyevent','4');time.sleep(.6)

def start_location():
    adb('shell','am','start','-n',PKG+'/.MainActivity')
    tap('Buka Lokasi');wait_text('Lokasi Saya')

def success():
    return wait(lambda r: any(t.startswith('Latitude:') for t in labels(r)) and 'Mengambil lokasi...' not in labels(r), seconds=32)

def stamp(r):
    return next(t for t in labels(r) if t.startswith('Terakhir diperbarui:'))

mode = sys.argv[1]
if mode in ['fulltrial', 'finish', 'permissions']:
    cases = ['precise', 'approximate', 'off', 'denied', 'precise'] if mode == 'fulltrial' else (['off', 'denied', 'precise'] if mode == 'finish' else ['denied', 'precise'])
    for case in cases:
        subprocess.check_call([sys.executable, str(Path(__file__).resolve()), case])
    sys.exit(0)
if mode == 'initial':
    start_location();wait_text('Lokasi belum diminta');shot('01-idle.png')
    tap('Ambil Lokasi Saya')
    wait(lambda r: any('permission_allow_foreground_only_button' in n.get('resource-id','') for n in r.iter('node')))
    shot('02-dialog.png')
    print(labels(dump()),flush=True)
elif mode == 'denied':
    r = dump()
    if not any(n.get('text') == "Don't allow" for n in r.iter('node')):
        for permission in ['android.permission.ACCESS_FINE_LOCATION', 'android.permission.ACCESS_COARSE_LOCATION']:
            subprocess.run(['adb','shell','pm','revoke',PKG,permission],check=False,stdout=subprocess.DEVNULL)
        adb('shell','am','force-stop',PKG)
        start_location();tap('Ambil Lokasi Saya')
    tap("Don't allow")
    wait_text('Minta Izin Lagi');shot('05-denied.png')
    tap('Minta Izin Lagi')
    r = dump()
    if not any('permission_allow_foreground_only_button' in n.get('resource-id','') for n in r.iter('node')):
        assert 'Buka Pengaturan' in labels(r)
        print('Penolakan permanen terdeteksi; opsi Buka Pengaturan tersedia.',flush=True)
        # Reset only this lab app's denial flags to test another runtime-permission grant.
        for permission in ['android.permission.ACCESS_FINE_LOCATION', 'android.permission.ACCESS_COARSE_LOCATION']:
            adb('shell','pm','clear-permission-flags',PKG,permission,'user-set','user-fixed')
        tap('Minta Izin Lagi')
    wait(lambda r: any('permission_allow_foreground_only_button' in n.get('resource-id','') for n in r.iter('node')))
    print('LULUS: Denied tanpa crash dan Minta Izin Lagi.',flush=True)
elif mode == 'precise':
    r = dump()
    fine = next((n for n in r.iter('node') if n.get('text') == 'Precise'),None)
    if fine is not None: tap_node(fine)
    if any('permission_allow_foreground_only_button' in n.get('resource-id','') for n in r.iter('node')):
        tap_id('permission_allow_foreground_only_button')
    wait_text('Jenis akses: Precise')
    r = success();shot('03-precise.png')
    old = stamp(r);time.sleep(1.1)
    tap('Perbarui Lokasi');r = success()
    assert stamp(r) != old, (old,stamp(r))
    assert not any('permissioncontroller' in n.get('package','') for n in r.iter('node'))
    shot('07-precise-refreshed.png')
    print('LULUS: Precise, accuracy, timestamp berubah, refresh tanpa dialog ulang.',flush=True)
elif mode == 'approximate':
    adb('shell','pm','revoke',PKG,'android.permission.ACCESS_FINE_LOCATION')
    adb('shell','am','force-stop',PKG)
    start_location();wait_text('Jenis akses: Approximate')
    tap('Ambil Lokasi Saya');success();shot('04-approximate.png')
    (OUT/'izin-approximate.txt').write_bytes(adb('shell','dumpsys','package',PKG))
    print('LULUS: Approximate dengan COARSE tanpa FINE.',flush=True)
elif mode == 'off':
    def set_service(enabled):
        r = dump()
        if 'No location access' in labels(r) and 'Close' in labels(r): tap('Close')
        adb('shell','am','start','-a','android.settings.LOCATION_SOURCE_SETTINGS')
        r = wait(lambda r: any(n.get('resource-id','').endswith('switch_widget') for n in r.iter('node')))
        switch = next(n for n in r.iter('node') if n.get('resource-id','').endswith('switch_widget'))
        if (switch.get('checked') == 'true') != enabled: tap_node(switch)
        r = dump()
        if 'No location access' in labels(r) and 'Close' in labels(r): tap('Close')
        wait(lambda r: any(n.get('resource-id','').endswith('switch_widget') and (n.get('checked') == 'true') == enabled for n in r.iter('node')))
        adb('shell','am','start','--activity-reorder-to-front','-n',PKG+'/.MainActivity')
        r = dump()
        if 'Buka Lokasi' in labels(r): tap('Buka Lokasi')
        wait_text('Lokasi Saya')
        time.sleep(1)
    try:
        set_service(False)
        print('Location off via Settings:',adb('shell','cmd','location','is-location-enabled').decode().strip(),flush=True)
        tap('Perbarui Lokasi')
        wait_text('Layanan lokasi sedang nonaktif. Aktifkan Lokasi di perangkat, lalu coba lagi.')
        shot('06-location-off.png')
    finally:
        set_service(True)
    tap('Perbarui Lokasi');success();shot('09-retry-after-location-on.png')
    back();tap('Favorites');wait_text('Favorites');shot('08-regression-favorites.png')
    back();wait_text('Buka Lokasi')
    shot('10-regression-home.png')
    print('LULUS: Location off/error, retry, navigasi kembali dan Favorites.',flush=True)
else:
    raise ValueError(mode)
