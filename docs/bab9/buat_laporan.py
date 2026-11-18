from pathlib import Path
from copy import deepcopy
from lxml import etree as E
from PIL import Image, ImageDraw, ImageFont
import zipfile

ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'docs/bab9'; SH=OUT/'screenshots'
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
    im=Image.new('RGB',(1560,1760),'white');d=ImageDraw.Draw(im)
    for i,(file,label) in enumerate(items):
        x=(i%2)*780; y=(i//2)*880
        d.text((x+20,y+5),label,font=ImageFont.truetype(sans,25),fill='#111111')
        src=Image.open(SH/file).convert('RGB');src.thumbnail((740,810))
        im.paste(src,(x+(780-src.width)//2,y+45))
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
    if t.text:t.text=t.text.replace('Bab 07','Bab 09')
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
    count+=1; rid='rIdBAB9'+str(count);target='media/bab9_'+str(count)+'.png';media['word/'+target]=path.read_bytes()
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

p('LATIHAN / TUGAS AKHIR PRAKTIKUM',True,26)
p('Tambahkan FavoritesScreen yang menampilkan seluruh mahasiswa favorit dari Room dan terhubung ke Navigation Compose.',True,22)
p('1. Tambahkan route favorites pada struktur navigasi.',True)
p('ui/theme/routes.kt dan navigation/NavigationLabApp.kt')
code('const val FAVORITES = "favorites"')
p('Home menyediakan tombol Favorites. Destination favorites membuat FavoritesViewModel melalui factory dan mengoleksi uiState menggunakan collectAsStateWithLifecycle(). Tombol Kembali mengembalikan pengguna ke Home.')
p('2. FavoritesScreen mengamati daftar dari FavoriteRepository melalui ViewModel dan Flow/StateFlow.',True)
p('data/local/FavoriteStudentDao.kt')
code('@Query("SELECT * FROM favorite_students ORDER BY firstName COLLATE NOCASE ASC, id ASC")\nfun observeFavorites(): Flow<List<FavoriteStudentEntity>>')
p('RoomFavoriteRepository memetakan entity ke Student. FavoritesViewModel menggabungkan Flow daftar favorit dan preferensi urutan, kemudian mengekspos StateFlow<FavoritesUiState> read-only. UI hanya menerima state dan event.')
p('3. Daftar menampilkan minimal nama dan email mahasiswa favorit.',True)
p('screen/FavoritesScreen.kt')
code('Text(student.name, style = MaterialTheme.typography.titleMedium)\nText(student.email, style = MaterialTheme.typography.bodyMedium)')
p('Daftar menggunakan LazyColumn dengan key berupa ID. Bila belum ada data, tampil pesan untuk menyimpan profil melalui halaman Detail.')
p('4. Menekan item membuka DetailScreen mahasiswa terkait.',True)
p('navigation/NavigationLabApp.kt — event item Favorites')
code('onStudentClick = { id -> navController.navigate(Routes.detail(id)) },')
p('Detail menerima studentId dari route. Profil yang telah disimpan dapat dibaca kembali melalui FavoriteRepository, sehingga Detail favorit juga dapat dibuka tanpa request jaringan.')
p('5. Jika favorit dihapus dari DetailScreen, FavoritesScreen otomatis berubah tanpa refresh manual.',True)
p('DetailViewModel.kt — penghapusan melalui repository')
code('if (state.isFavorite) favoriteRepository.remove(student.id)\nelse favoriteRepository.add(student)')
p('Insert/delete Room memicu emisi Flow DAO. Saat kembali dari Detail, daftar Favorites langsung mengikuti isi tabel terbaru tanpa tombol refresh. Status tombol Simpan/Hapus di Detail juga mengikuti Flow dari Room.')
p('6. Tambahkan satu preferensi sederhana lain ke DataStore dan buktikan bertahan setelah restart.',True)
p('data/preferences/UserPreferencesRepository.kt')
code('private val sortAscendingKey = booleanPreferencesKey("sort_ascending")\noverride val sortAscending = preferences.map { it[sortAscendingKey] ?: true }\noverride suspend fun saveSortAscending(value: Boolean) {\n    dataStore.edit { it[sortAscendingKey] = value }\n}')
p('Switch Urutan nama memilih A–Z atau Z–A. Perubahan diteruskan ke FavoritesViewModel lalu repository DataStore. Flow preferensi mengurutkan daftar secara reaktif. Pilihan Z–A tetap muncul setelah force-stop dan aplikasi dibuka kembali.')
p('Batasan: composable tidak mengakses DAO atau DataStore. Akses storage dilakukan melalui repository dan ViewModel. Room menyimpan data favorit terstruktur; DataStore menyimpan preferensi sederhana.',size=20)
page()
p('LIST SCREENSHOT — LATIHAN PRAKTIKUM',True,25)
grid('bukti-latihan.png', [
    ('01-favorites-az.png','1. Daftar favorit: nama dan email'),
    ('02-detail-favorit.png','2. Item membuka Detail favorit'),
    ('04-sort-after-restart.png','3. Urutan Z–A setelah restart'),
    ('05-after-delete.png','4. Daftar berubah setelah hapus')
])
img(OUT/'bukti-latihan.png',6.2)
p('Pengujian: dua profil disimpan dari Detail; Favorites menampilkan nama dan email. Pilihan urutan diubah menjadi Z–A, lalu aplikasi dihentikan dan dibuka kembali. Preferensi dan data favorit tetap tersedia. Salah satu favorit dihapus melalui Detail; ketika kembali ke Favorites, daftar langsung berubah tanpa refresh manual.')
p('Screenshot diambil langsung dari HP Samsung SM-A325F. Source code, screenshot asli, dan catatan validasi tersimpan di docs/bab9.',size=18)
body.append(sect)
ct=E.fromstring(z.read('[Content_Types].xml'))
if not any(n.get('Extension')=='png' for n in ct):E.SubElement(ct,'{http://schemas.openxmlformats.org/package/2006/content-types}Default',Extension='png',ContentType='image/png')
output=ROOT/'Ezrasto Mahardika Maydiputra_245150200111003_BAB 9.docx'
with zipfile.ZipFile(output,'w',zipfile.ZIP_DEFLATED) as out:
    for name in z.namelist():
        data=z.read(name)
        if name=='word/document.xml':data=E.tostring(r,xml_declaration=True,encoding='UTF-8',standalone=True)
        elif name=='word/_rels/document.xml.rels':data=E.tostring(rels,xml_declaration=True,encoding='UTF-8',standalone=True)
        elif name=='[Content_Types].xml':data=E.tostring(ct,xml_declaration=True,encoding='UTF-8',standalone=True)
        out.writestr(name,data)
    for name,data in media.items():out.writestr(name,data)
print(output)
