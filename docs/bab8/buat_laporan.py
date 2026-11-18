from pathlib import Path
from copy import deepcopy
from lxml import etree as E
from PIL import Image, ImageDraw, ImageFont
import zipfile

ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'docs/bab8'; SH=OUT/'screenshots'
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
b=ROOT/'app/src/main/java/com/example/bab6'
code_image('01-service.png','1. StudentApiService.kt — cuplikan source implementasi',b/'data/remote/StudentApiService.kt',10,23)
code_image('02-viewmodel.png','2. HomeViewModel.kt — cuplikan source implementasi',b/'ui/home/HomeViewModel.kt',13,32)

def grid(filename,items):
    im=Image.new('RGB',(1560,1760),'white');d=ImageDraw.Draw(im)
    for i,(file,label) in enumerate(items):
        x=(i%2)*780; y=(i//2)*880
        d.text((x+20,y+5),label,font=ImageFont.truetype(sans,25),fill='#111111')
        src=Image.open(SH/file).convert('RGB');src.thumbnail((740,810))
        im.paste(src,(x+(780-src.width)//2,y+45))
    im.save(OUT/filename)

grid('hasil-data.png', [('03-home.png','3. Home: 10 profil awal'),('04-search.png','4. Pencarian otomatis: john'),('11-detail-john.png','5. Detail hasil pencarian: ID 102'),('10-loading.png','Tambahan: loading saat Refresh')])
grid('hasil-refresh.png', [('06-error.png','6. Error saat Wi-Fi dan data mati'),('07-retry.png','7. Berhasil setelah Coba Lagi'),('08-before-refresh.png','8. Sebelum Refresh: query john'),('09-after-refresh.png','9. Sesudah Refresh: query tetap john')])

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
    if t.text:t.text=t.text.replace('Bab 07','Bab 08')
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
    count+=1; rid='rIdBAB8'+str(count);target='media/bab8_'+str(count)+'.png';media['word/'+target]=path.read_bytes()
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

p('TUGAS PRAKTIKUM',True,26)
p('Tambahkan fitur Refresh yang menggunakan coroutine dan mempertahankan pola StateFlow.',True,22)
p('1. Tambahkan tombol Refresh pada HomeScreen.',True)
p('HomeScreen.kt')
code('Button(onClick = onRefresh, enabled = !uiState.isLoading) {\n    Text("Refresh")\n}')
p('2. Event tombol harus memanggil fungsi refresh() di HomeViewModel.',True)
p('NavigationLabApp.kt')
code('onRefresh = homeViewModel::refresh,')
p('Tombol meneruskan event melalui parameter onRefresh. HomeScreen tidak mengakses repository secara langsung.')
p('3. refresh() harus menggunakan viewModelScope.launch.',True)
p('HomeViewModel.kt')
code('fun refresh() {\n    requestJob?.cancel()\n    requestJob = viewModelScope.launch {\n        fetchStudents(searchQuery.value.trim())\n    }\n}')
p('Request yang masih berjalan dibatalkan sebelum coroutine baru dijalankan agar hasil lama tidak mengganti hasil Refresh.')
p('4. Jika searchQuery kosong, refresh memuat daftar awal.',True)
p('5. Jika searchQuery berisi teks, refresh mengulang pencarian dengan query aktif.',True)
p('HomeViewModel.kt — pemilihan request di dalam fetchStudents(query)')
code('val students = if (query.isBlank()) repository.getStudents()\n    else repository.searchStudents(query)')
p('Query kosong memuat 10 profil awal. Query john memuat ulang hasil pencarian john tanpa menghapus teks pencarian.')
p('6. State isLoading dan errorMessage harus diperbarui dengan benar.',True)
p('HomeViewModel.kt — pembaruan StateFlow di dalam fetchStudents(query)')
code('_uiState.value = _uiState.value.copy(\n    isLoading = true, errorMessage = null\n)\ntry {\n    val students = if (query.isBlank()) repository.getStudents()\n        else repository.searchStudents(query)\n    _uiState.value = HomeUiState(students = students)\n} catch (e: CancellationException) {\n    throw e\n} catch (e: Exception) {\n    _uiState.value = HomeUiState(\n        errorMessage = e.message ?: "Gagal mengambil data"\n    )\n}')
p('Saat request dimulai, loading aktif dan error dibersihkan. Saat selesai, HomeUiState mengakhiri loading; jika gagal, pesan error ditampilkan. State tetap menggunakan MutableStateFlow private dan StateFlow read-only.')
p('7. Jangan membuat CoroutineScope baru di HomeScreen.',True)
p('8. Jangan menggunakan GlobalScope.',True)
p('HomeScreen hanya memanggil onRefresh. Seluruh proses asinkron berada di HomeViewModel melalui viewModelScope, sehingga tidak memerlukan CoroutineScope baru atau GlobalScope.')
page()
p('TUGAS PRAKTIKUM — HASIL PENGUJIAN',True,25)
p('9. Setelah refresh selesai, aplikasi tetap dapat membuka Detail dan kembali ke Home.',True)
p('Pada HP Samsung A32, Refresh dengan query john tetap menampilkan Emily Johnson, John Doe, dan Michael Johnson. Memilih John Doe membuka Detail ID 102 dengan email dan universitas yang sesuai. Tombol kembali mengembalikan pengguna ke Home dengan query tetap john. Refresh dengan query kosong juga telah diuji dan menampilkan 10 profil awal.')
p('10. Tambahkan satu screenshot sebelum dan sesudah Refresh pada laporan.',True)
p('LIST SCREENSHOT',True,23)
grid('tugas-refresh.png', [
    ('08-before-refresh.png','Screenshot 1 — Sebelum Refresh'),
    ('09-after-refresh.png','Screenshot 2 — Sesudah Refresh'),
    ('10-loading.png','Screenshot 3 — Loading saat Refresh'),
    ('11-detail-john.png','Screenshot 4 — Detail setelah Refresh')
])
img(OUT/'tugas-refresh.png',6.2)
p('Screenshot diambil langsung dari HP Samsung SM-A325F. Sebelum dan sesudah Refresh, query john dan hasilnya tetap sama karena data API tidak berubah. Indikator loading menunjukkan proses pemuatan ulang berjalan.',size=20)
body.append(sect)
ct=E.fromstring(z.read('[Content_Types].xml'))
if not any(n.get('Extension')=='png' for n in ct):E.SubElement(ct,'{http://schemas.openxmlformats.org/package/2006/content-types}Default',Extension='png',ContentType='image/png')
output=ROOT/'Ezrasto Mahardika Maydiputra_245150200111003_BAB 8.docx'
with zipfile.ZipFile(output,'w',zipfile.ZIP_DEFLATED) as out:
    for name in z.namelist():
        data=z.read(name)
        if name=='word/document.xml':data=E.tostring(r,xml_declaration=True,encoding='UTF-8',standalone=True)
        elif name=='word/_rels/document.xml.rels':data=E.tostring(rels,xml_declaration=True,encoding='UTF-8',standalone=True)
        elif name=='[Content_Types].xml':data=E.tostring(ct,xml_declaration=True,encoding='UTF-8',standalone=True)
        out.writestr(name,data)
    for name,data in media.items():out.writestr(name,data)
print(output)
