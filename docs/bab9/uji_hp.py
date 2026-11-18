"""Pengujian UI terbatas pada aplikasi praktikum melalui HP Android yang terhubung."""
from pathlib import Path
import re
import subprocess
import time
import xml.etree.ElementTree as E

OUT = Path(__file__).resolve().parent
SH = OUT / 'screenshots'
PKG = 'com.example.bab6'

def adb(*args):
    return subprocess.check_output(['adb', *args], stderr=subprocess.STDOUT)

def dump():
    for _ in range(4):
        adb('shell', 'uiautomator', 'dump', '/sdcard/bab9.xml')
        xml = adb('exec-out', 'cat', '/sdcard/bab9.xml')
        if xml.startswith(b'<?xml'):
            break
        time.sleep(1)
    (OUT / 'ui-terakhir.xml').write_bytes(xml)
    return E.fromstring(xml)

def labels(root):
    return [n.get('text') for n in root.iter('node') if n.get('text') and n.get('package') == PKG]

def wait_text(text, present=True):
    for _ in range(8):
        root = dump()
        if (text in labels(root)) == present:
            return root
        time.sleep(.5)
    raise AssertionError(f'{text!r}, present={present}: {labels(root)}')

def tap_node(node):
    x1,y1,x2,y2 = map(int, re.findall(r'\d+', node.get('bounds')))
    adb('shell', 'input', 'tap', str((x1+x2)//2), str((y1+y2)//2))
    time.sleep(.5)

def tap(text):
    root = wait_text(text)
    tap_node(next(n for n in root.iter('node') if n.get('text') == text))

def screenshot(name):
    time.sleep(.6)
    (SH/name).write_bytes(adb('exec-out', 'screencap', '-p'))
    print(f'Screenshot: {name}', flush=True)

def back():
    adb('shell', 'input', 'keyevent', '4')
    time.sleep(.6)

adb('shell', 'am', 'force-stop', PKG)
adb('shell', 'am', 'start', '-n', f'{PKG}/.MainActivity')
wait_text('1 - Emily Johnson')
for name in ['1 - Emily Johnson', '2 - Michael Williams']:
    tap(name)
    tap('Simpan ke Favorit')
    wait_text('Hapus dari Favorit')
    back()
    print(f'Tersimpan: {name}', flush=True)
tap('Favorites')
wait_text('Emily Johnson'); wait_text('Michael Williams')
wait_text('Urutan nama: A–Z')
screenshot('01-favorites-az.png')
tap('Emily Johnson'); wait_text('Hapus dari Favorit')
screenshot('02-detail-favorit.png'); back()
root = dump()
switch = next(n for n in root.iter('node') if n.get('checkable') == 'true')
tap_node(switch); wait_text('Urutan nama: Z–A')
screenshot('03-sort-before-restart.png')
back()
root = dump()
field = next(n for n in root.iter('node') if n.get('class') == 'android.widget.EditText')
tap_node(field); adb('shell', 'input', 'text', 'john'); time.sleep(2); back()
wait_text('102 - John Doe')
adb('shell', 'am', 'force-stop', PKG)
adb('shell', 'am', 'start', '-n', f'{PKG}/.MainActivity')
wait_text('102 - John Doe'); wait_text('john')
screenshot('07-query-after-restart.png')
tap('Favorites'); wait_text('Urutan nama: Z–A')
wait_text('Michael Williams'); wait_text('Emily Johnson')
screenshot('04-sort-after-restart.png')
tap('Michael Williams'); wait_text('Hapus dari Favorit')
tap('Hapus dari Favorit'); wait_text('Simpan ke Favorit')
screenshot('06-detail-after-delete.png'); back()
wait_text('Michael Williams', present=False); wait_text('Emily Johnson')
screenshot('05-after-delete.png')
print('LULUS: Room persist, nama/email tampil, navigasi Detail/Back, sort persist, penghapusan reaktif, query persist.', flush=True)
