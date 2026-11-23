from pathlib import Path
from copy import deepcopy
from lxml import etree as E
from PIL import Image, ImageDraw, ImageFont
import zipfile

ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'docs/bab10'; SH=OUT/'screenshots'
font='/usr/share/fonts/google-noto/NotoSansMono-Regular.ttf'
sans='/usr/share/fonts/liberation-sans-fonts/LiberationSans-Regular.ttf'

def code_image(name,title,source,first,last):
    lines=source.read_text().splitlines()[first-1:last]
    f=ImageFont.truetype(font,19)
    im=Image.new('RGB',(1480,76+len(lines)*27),'#f6f8fa');d=ImageDraw.Draw(im)
    d.rectangle((0,0,1480,53),fill='#e4e9ef');d.text((18,12),title,font=ImageFont.truetype(sans,23),fill='#142133')
    for i,line in enumerate(lines):d.text((18,65+i*27),f'{first+i:02}  {line}',font=f,fill='#172536')
    im.save(SH/name)
    return im
def grid(filename,items):
    im=Image.new('RGB',(1800,1840),'white');d=ImageDraw.Draw(im)
    for i,(file,label) in enumerate(items):
        x=(i%3)*600; y=(i//3)*920
        d.text((x+12,y+5),label,font=ImageFont.truetype(sans,24),fill='#111111')
        src=Image.open(SH/file).convert('RGB');src.thumbnail((580,860))
        im.paste(src,(x+(600-src.width)//2,y+43))
    im.save(OUT/filename)

W='http://schemas.openxmlformats.org/wordprocessingml/2006/main'; R='http://schemas.openxmlformats.org/officeDocument/2006/relationships'; PR='http://schemas.openxmlformats.org/package/2006/relationships'; NS={'w':W}
def el(tag,**attrs):
    n=E.Element('{'+W+'}'+tag)
    for k,v in attrs.items():n.set('{'+W+'}'+k,str(v))
    return n
z=zipfile.ZipFile(ROOT/'Ezrasto Mahardika Maydiputra_245150200111003_BAB 7.docx')
r=E.fromstring(z.read('word/document.xml')); body=r.find('w:body',NS)
sect=deepcopy(body[-1])
for node in list(body)[19:]:body.remove(node)
for t in body.xpath('.//w:t',namespaces=NS):
    if t.text:t.text=t.text.replace('Bab 07','Bab 10')
rels=E.fromstring(z.read('word/_rels/document.xml.rels'))
media={};count=100

def p(text='',bold=False,size=20):
    n=el('p'); pr=el('pPr');pr.append(el('spacing',after=55,line=230,lineRule='auto'));n.append(pr)
    run=el('r');rp=el('rPr');rp.append(el('rFonts',ascii='Times New Roman',hAnsi='Times New Roman'));rp.append(el('sz',val=size))
    if bold:rp.append(el('b'))
    run.append(rp);t=el('t');t.set('{http://www.w3.org/XML/1998/namespace}space','preserve');t.text=text;run.append(t);n.append(run);body.append(n);return n

def page():
    n=el('p');run=el('r');run.append(el('br',type='page'));n.append(run);body.append(n)

def img(path,width):
    global count
    count+=1; rid='rIdBAB10'+str(count);target='media/bab10_'+str(count)+'.png';media['word/'+target]=path.read_bytes()
    rel=E.SubElement(rels,'{'+PR+'}Relationship',Id=rid,Type=R+'/image',Target=target)
    im=Image.open(path);cx=int(width*914400);cy=int(cx*im.height/im.width)
    n=p();pr=n.find('w:pPr',NS);pr.remove(pr.find('w:spacing',NS));pr.append(el('spacing',before=90,after=90,line=240,lineRule='auto'));pr.append(el('jc',val='center'))
    xml=f'''<w:r xmlns:w="{W}" xmlns:r="{R}" xmlns:wp="http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing" xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main" xmlns:pic="http://schemas.openxmlformats.org/drawingml/2006/picture"><w:drawing><wp:inline distT="0" distB="0" distL="0" distR="0"><wp:extent cx="{cx}" cy="{cy}"/><wp:docPr id="{count}" name="{path.name}"/><wp:cNvGraphicFramePr/><a:graphic><a:graphicData uri="http://schemas.openxmlformats.org/drawingml/2006/picture"><pic:pic><pic:nvPicPr><pic:cNvPr id="0" name="{path.name}"/><pic:cNvPicPr/></pic:nvPicPr><pic:blipFill><a:blip r:embed="{rid}"/><a:stretch><a:fillRect/></a:stretch></pic:blipFill><pic:spPr><a:xfrm><a:off x="0" y="0"/><a:ext cx="{cx}" cy="{cy}"/></a:xfrm><a:prstGeom prst="rect"><a:avLst/></a:prstGeom></pic:spPr></pic:pic></a:graphicData></a:graphic></wp:inline></w:drawing></w:r>'''
    n.append(E.fromstring(xml))

def code(text):
    for line in text.splitlines():
        n=p(line,size=18)
        pr=n.find('w:pPr',NS)
        pr.find('w:spacing',NS).set('{'+W+'}after','0')
        pr.append(el('shd',fill='F2F2F2'))
        rp=n.find('w:r/w:rPr',NS)
        rp.find('w:rFonts',NS).set('{'+W+'}ascii','Courier New')
        rp.find('w:rFonts',NS).set('{'+W+'}hAnsi','Courier New')

p('LATIHAN / TUGAS PRAKTIKUM',True,26)
p('Kembangkan fitur lokasi agar lebih informatif tanpa menambah API peta eksternal.',True,22)
p('1. Tambahkan label jenis akses: Precise jika ACCESS_FINE_LOCATION tersedia, selain itu Approximate.',True)
p('data/location/DeviceLocation.kt — penentuan label dari izin aktif')
code('fun fromPermissions(fine: Boolean, coarse: Boolean): LocationAccess = when {\n    fine -> PRECISE\n    coarse -> APPROXIMATE\n    else -> NONE\n}')
p('ui/location/LocationScreen.kt')
code('Text("Jenis akses: ${uiState.access.label}")')
p('Status izin diperiksa saat layar aktif dan setiap tombol ditekan. Tanpa izin, label menjadi Belum diberikan. Izin COARSE saja tetap diterima; pengguna tidak dipaksa memberikan Precise.')
p('2. Tampilkan accuracy dalam meter dan waktu terakhir lokasi berhasil diperbarui.',True)
p('ui/location/LocationViewModel.kt — pembaruan state saat request berhasil')
code('_uiState.update { it.copy(\n    location = location, lastUpdatedMillis = nowMillis(), isLoading = false\n) }')
p('ui/location/LocationScreen.kt')
code('Text("Accuracy: ${location.accuracy?.let {\n    String.format(Locale.getDefault(), "%.1f m", it)\n} ?: "Tidak tersedia"}")')
p('Waktu keberhasilan ditampilkan dengan format dd-MM-yyyy HH:mm:ss. Saat belum ada hasil, tertulis Belum ada pembaruan berhasil. Request gagal tidak mengganti waktu keberhasilan sebelumnya.')
p('3. Tambahkan tombol Perbarui Lokasi tanpa membuka dialog izin lagi jika izin masih tersedia.',True)
p('ui/location/LocationScreen.kt — alur tombol pada requestLocation()')
code('val access = currentAccess()\nviewModel.onPermissionChanged(access)\nif (access != LocationAccess.NONE) {\n    viewModel.refreshLocation()\n} else {\n    permissionLauncher.launch(arrayOf(\n        Manifest.permission.ACCESS_COARSE_LOCATION,\n        Manifest.permission.ACCESS_FINE_LOCATION\n    ))\n}')
code('Button(onClick = ::requestLocation, enabled = !uiState.isLoading) {\n    Text(if (uiState.location != null || uiState.errorMessage != null)\n        "Perbarui Lokasi" else "Ambil Lokasi Saya")\n}')
p('Tombol Perbarui Lokasi memakai alur yang sama dan langsung memanggil refreshLocation() bila izin masih tersedia. ViewModel menjalankan request melalui viewModelScope dan mengekspos StateFlow read-only.')
p('4. Tambahkan pesan yang jelas ketika permission ditolak dan tombol Minta Izin Lagi.',True)
p('ui/location/LocationScreen.kt')
code('Text("Izin lokasi ditolak. Berikan izin untuk mengambil lokasi perangkat.")\nButton(onClick = ::requestLocation) { Text("Minta Izin Lagi") }')
p('Jika izin ditolak, repository tidak dipanggil. Tombol meminta izin ulang melalui Activity Result API. Buka Pengaturan juga disediakan bila dialog tidak muncul karena penolakan permanen.')
p('5. Pastikan aplikasi stabil ketika lokasi tidak tersedia atau hanya Approximate.',True)
p('data/location/DefaultLocationRepository.kt')
code('val priority = if (fineGranted) Priority.PRIORITY_HIGH_ACCURACY\n    else Priority.PRIORITY_BALANCED_POWER_ACCURACY\nval location = withTimeoutOrNull(20_000L) {\n    client.getCurrentLocation(priority, cancellation.token).await()\n} ?: error("Lokasi belum tersedia. Pastikan layanan Lokasi aktif, lalu coba lagi.")')
p('Repository memeriksa ulang permission dan layanan Lokasi. Hasil null, timeout, dan error ditampilkan tanpa crash. CancellationException diteruskan; request dibatalkan saat layar tidak aktif. Hanya foreground location dan satu pembacaan lokasi digunakan.')
page()
p('LIST SCREENSHOT — LATIHAN PRAKTIKUM',True,25)
grid('bukti-latihan.png', [
    ('01-idle.png','1. Sebelum lokasi diminta'),
    ('02-dialog.png','2. Dialog izin lokasi'),
    ('03-precise.png','3. Hasil Precise'),
    ('04-approximate.png','4. Hasil Approximate'),
    ('05-denied.png','5. Izin ditolak / izin ulang'),
    ('06-location-off.png','6. Layanan lokasi nonaktif')
])
img(OUT/'bukti-latihan.png',6.3)
p('Pengujian dilakukan pada Samsung SM-A325F: label izin, koordinat, accuracy, waktu keberhasilan, Perbarui Lokasi tanpa dialog ulang, penolakan dan permintaan izin ulang, serta error saat layanan Lokasi nonaktif. Screenshot asli dan catatan hasil tersimpan di docs/bab10.')
p('Kendala dan solusi: izin dapat berubah melalui Settings. Status diperiksa ulang saat ON_RESUME dan setiap klik; hasil Precise lama dibersihkan ketika izin diturunkan menjadi Approximate. Pembacaan lokasi dibatasi 20 detik agar UI tidak terus berada pada loading.',size=20)
body.append(sect)
ct=E.fromstring(z.read('[Content_Types].xml'))
if not any(n.get('Extension')=='png' for n in ct):E.SubElement(ct,'{http://schemas.openxmlformats.org/package/2006/content-types}Default',Extension='png',ContentType='image/png')
output=ROOT/'Ezrasto Mahardika Maydiputra_245150200111003_BAB 10.docx'
with zipfile.ZipFile(output,'w',zipfile.ZIP_DEFLATED) as out:
    for name in z.namelist():
        data=z.read(name)
        if name=='word/document.xml':data=E.tostring(r,xml_declaration=True,encoding='UTF-8',standalone=True)
        elif name=='word/_rels/document.xml.rels':data=E.tostring(rels,xml_declaration=True,encoding='UTF-8',standalone=True)
        elif name=='[Content_Types].xml':data=E.tostring(ct,xml_declaration=True,encoding='UTF-8',standalone=True)
        out.writestr(name,data)
    for name,data in media.items():out.writestr(name,data)
print(output)
