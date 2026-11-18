from pathlib import Path
import sys, csv, os
os.environ['MPLCONFIGDIR']='/tmp/detektif-mpl'
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from scipy.signal import welch, find_peaks
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, Image
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.enums import TA_LEFT

HERE=Path(__file__).resolve().parent
SRC=Path('/home/astopoi/Downloads/untuk_mahasiswa/praktikum_seluler')
sys.path.insert(0,str(SRC))
from seluler_dasar import baca_cs8
from bentuk_sinyal import autokorelasi, lebar_terisi
OUT=HERE/'hasil'
for n,fs,fc in [(1,20e6,2329.8),(2,20e6,2050),(3,20e6,1870),(5,15.36e6,945.2)]:
    x,_=baca_cs8(SRC/f'data/misteri/misteri_{n}.cs8',fs)
    f,p=welch(x[:int(.2*fs)],fs,nperseg=4096,return_onesided=False)
    order=np.argsort(f);f=f[order];p=10*np.log10(p[order]+1e-12)
    lo,hi,_=lebar_terisi(f,p)
    fig,ax=plt.subplots(2,1,figsize=(10,5.0),layout='constrained')
    ax[0].plot(fc+f/1e6,p-np.median(p),color='#16354b',lw=.8)
    ax[0].set(xlabel='Frekuensi absolut (MHz)',ylabel='PSD relatif median (dB)',title=f'Spektrum rekaman {n}')
    if n==2:
        peaks,_=find_peaks(p,prominence=4)
        labels=[fc+f[i]/1e6 for i in peaks if p[i]-np.median(p)>4]
        (OUT/'misteri_2_spur.txt').write_text(str(labels))
        for v in labels:
            if abs(v-round(v))<.02: ax[0].axvline(v,color='#e8663d',alpha=.2)
        r=autokorelasi(x,fs,lo,hi); start=int(fs*20e-6)
        ax[1].plot(np.arange(start,len(r))/fs*1e6,r[start:]/np.median(r[start:]),color='#e8663d',lw=.8)
        ax[1].set(xlabel='Lag (µs)',ylabel='R / median R',title='Autokorelasi: puncak lemah, tidak membuktikan OFDM')
    else:
        step=int(fs*.0001);k=int(fs*.04)//step
        power=(np.abs(x[:step*k])**2).reshape(k,step).mean(axis=1)
        ax[1].plot((np.arange(k)+.5)*step/fs*1000,10*np.log10(power/power.max()),color='#e8663d',lw=1)
        ax[1].set(xlabel='Waktu setelah transien dibuang (ms)',ylabel='Daya relatif (dB)',title='Selubung daya; rata-rata per 0,1 ms')
    for a in ax: a.grid(alpha=.18)
    fig.savefig(OUT/f'misteri_{n}_laporan.png',dpi=165);plt.close(fig)

FONT='/usr/share/fonts/liberation-sans-fonts/'
pdfmetrics.registerFont(TTFont('LS',FONT+'LiberationSans-Regular.ttf'))
pdfmetrics.registerFont(TTFont('LSB',FONT+'LiberationSans-Bold.ttf'))
pdfmetrics.registerFontFamily('LS',normal='LS',bold='LSB',italic='LS',boldItalic='LSB')
styles=getSampleStyleSheet()
styles.add(ParagraphStyle(name='BodyID',fontName='LS',fontSize=10.2,leading=14.5,spaceAfter=8,textColor=colors.HexColor('#213747')))
styles.add(ParagraphStyle(name='TitleID',fontName='LSB',fontSize=30,leading=34,spaceAfter=16,textColor=colors.HexColor('#132b3e')))
styles.add(ParagraphStyle(name='HeadID',fontName='LSB',fontSize=20,leading=24,spaceAfter=13,textColor=colors.HexColor('#132b3e')))
styles.add(ParagraphStyle(name='SubID',fontName='LSB',fontSize=12,leading=16,spaceBefore=7,spaceAfter=6,textColor=colors.HexColor('#ba4c2b')))
styles.add(ParagraphStyle(name='SmallID',fontName='LS',fontSize=8.2,leading=11,spaceAfter=6,textColor=colors.HexColor('#526777')))
story=[]
def p(t,style='BodyID'):story.append(Paragraph(t,styles[style]))
def h(t):p(t,'HeadID')
def sub(t):p(t,'SubID')
def page():story.append(PageBreak())
def table(rows,widths):
    data=[[Paragraph(str(c),styles['SmallID']) for c in row] for row in rows]
    t=Table(data,colWidths=widths,hAlign='LEFT',repeatRows=1)
    t.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),colors.HexColor('#e5edf3')),('ROWBACKGROUNDS',(0,1),(-1,-1),[colors.white,colors.HexColor('#f4f7f9')]),('VALIGN',(0,0),(-1,-1),'TOP'),('LEFTPADDING',(0,0),(-1,-1),8),('RIGHTPADDING',(0,0),(-1,-1),8),('TOPPADDING',(0,0),(-1,-1),7),('BOTTOMPADDING',(0,0),(-1,-1),5),('LINEBELOW',(0,0),(-1,0),.7,colors.HexColor('#93a9ba'))]))
    story.append(t);story.append(Spacer(1,10))
def graphic(path,caption,width=495):
    from PIL import Image as PILImage
    with PILImage.open(path) as im:w,h=im.size
    story.append(Image(str(path),width=width,height=width*h/w))
    p(caption,'SmallID')

p('<b>Nama:</b> Ezrasto Mahardika Maydiputra<br/><b>NIM:</b> 245150200111003')
p('LAPORAN ANALISIS BUKTI RADIO','SubID')
p('Detektif Seluler<br/>Kasus 1 &amp; 2','TitleID')
p('CIF65217 · Jaringan Nirkabel · Take-home Bab 5')
p('Disusun dari soal HTML, metadata rekaman, dan analisis langsung berkas IQ. Tanggal penyusunan: 8 November 2026.','SmallID')
sub('Hasil utama')
p('<b>Kasus 1:</b> sembilan sel pada inventaris titik A tidak berarti sembilan tower. Batas bawah yang dapat dibuktikan ialah <b>dua eNodeB</b>. Jumlah lokasi fisik tower dan tower yang melayani kampus belum dapat ditetapkan dari data radio ini saja.')
table([['Rekaman','Identifikasi','Kanal / mode','PCI'],['1','LTE B40','20 MHz · TDD','278'],['2','Noise + garis spur','Tidak berlaku','—'],['3','LTE B3','20 MHz · FDD','54, 202, 419'],['4','GSM DCS 1800','200 kHz per carrier · FDD','Bukan PCI LTE'],['5','LTE B8','10 MHz · FDD','16']],[55,150,175,115])
sub('Cakupan dan status kelengkapan')
p('Kasus 1 bagian A dan seluruh lima laporan forensik Kasus 2 dijawab berdasarkan bukti yang tersedia. <b>Kasus 1 bagian B belum dapat diselesaikan secara empiris</b>: folder referensi tidak memuat pengukuran ponsel pada tiga titik, koordinat kampus, atau eNB ID. Halaman 3 menyediakan tabel kerja dan cara menafsirkan hasilnya; tabel itu bukan data pengukuran.')
p('Pembahasan dibatasi pada Kasus 1 dan 2 sesuai permintaan. Tidak ada identitas pelanggan, isi komunikasi, atau lokasi perangkat orang lain yang dianalisis.','SmallID')
page()
h('Kasus 1 · A. Dari PCI ke eNodeB')
sub('1. PCI 16 di empat carrier')
p('PCI 16 tercatat pada 945,2; 1847,5; 2117,5; dan 2130,0 MHz, semuanya berjam A. Ini <b>konsisten dengan satu sektor yang memakai beberapa carrier</b>, sehingga empat kemunculan itu tidak harus dihitung sebagai empat site. Perencanaan PCI yang selaras lintas carrier memudahkan pengelolaan dan pemetaan sektor. Namun PCI hanya identitas fisik lokal yang dapat digunakan ulang; kecocokan PCI dan jam belum membuktikan satu eNodeB atau satu tower.')
sub('2. Sel yang pasti berbeda pada 1870 MHz')
table([['PCI','Awal frame (ms)','SFN','Jam'],['54','5,396','855','A'],['202','4,849','833','B'],['419','4,849','833','B']],[65,160,110,160])
p('Dalam <b>satu rekaman yang sama</b>, PCI 54 berbeda dari PCI 202 dan PCI 419: selisih awal frame 0,547 ms (sekitar 0,55 ms) dan SFN berbeda 22. Dengan model jam eNodeB pada soal, PCI 54 pasti berasal dari eNodeB yang berbeda dari kedua sel itu. Bukti pembeda ini lebih kuat daripada hanya melihat PCI yang berlainan.')
sub('3. PCI 202 dan 419: satu site atau dua?')
p('Keduanya mempunyai timing, SFN, dan jam B yang sama. Hipotesis paling sederhana ialah dua sel/sektor pada satu eNodeB atau site, tetapi <b>belum pasti</b>. N_ID_1 = 67 dan 139 hanya kelompok identitas fisik, bukan ID tower. PCI 202 = 3 × 67 + 1; PCI 419 = 3 × 139 + 2. Dua eNodeB berbeda juga bisa tersinkron. Keyakinan bahwa keduanya satu eNodeB: <b>sedang</b>; perlu ECGI/eNB ID atau pemetaan lapangan untuk memastikan.')
sub('4. Minimum jumlah eNodeB')
p('<b>Minimum terbukti: 2 eNodeB.</b> Rantai bukti: (a) pada 1870 MHz ada sel dengan jam A dan B yang berbeda dalam satu rekaman; (b) karena itu diperlukan sekurangnya dua eNodeB; (c) PCI 202 dan 419 belum terbukti berbeda eNodeB; (d) sel lintas carrier yang berjam A/B dapat dikelompokkan tanpa memaksa tambahan eNodeB. Ini batas bawah, bukan jumlah aktual yang pasti.')
p('<b>eNodeB ≠ lokasi tower.</b> Beberapa eNodeB dapat berada di satu lokasi fisik. Maka bukti ini tidak menetapkan minimum dua tower fisik. Jam A yang cocok GPS juga tidak menyatukan semua sel A: eNodeB yang berbeda dapat sama-sama tersinkron GPS.','SmallID')
page()
h('Kasus 1 · B. Pengukuran lapangan')
p('<b>Status: data lapangan belum tersedia.</b> Berkas IQ misteri tidak memuat operator SIM ponsel, RSRP/TA ponsel, eNB ID, atau koordinat tiga titik kampus. Karena itu nama/lokasi tower layanan dan peta kampus tidak dapat ditentukan secara sah dari berkas tersebut.')
sub('Tabel kerja yang perlu dilengkapi')
p('Pada tiga titik umum kampus, catat waktu dan koordinat titik, lalu salin nilai dari NetMonster atau Network Cell Info Lite. Tanda “—” di bawah berarti belum tersedia, bukan nol. Identitas sel tetangga dan TA sering tidak ditampilkan oleh ponsel.','SmallID')
rows=[['Titik / sel','Operator','EARFCN / PCI','RSRP (dBm)','TA','eNB ID']]
for titik in ['P1','P2','P3']:
    for sel in ['layanan','tetangga 1','tetangga 2']:rows.append([f'{titik} / {sel}','—','—','—','—','—'])
table(rows,[105,75,100,85,40,90])
sub('Jawaban metode: TA dibandingkan dengan peta')
p('Untuk sel layanan, perkiraan jarak menurut petunjuk soal adalah <b>d ≈ TA × 78 meter</b>. Setelah eNB ID ditemukan di CellMapper dengan operator dan jaringan LTE yang sesuai, ukur jarak garis lurus antara titik ukur dan lokasi tower pada peta. Catat d_TA, d_peta, dan selisihnya untuk tiap titik. TA tidak tersedia tidak boleh diisi nol.')
p('Perbedaan jarak dapat berasal dari kuantisasi TA, lintasan pantulan/NLOS yang lebih panjang daripada jarak lurus, keterlambatan pembaruan pembacaan, handover saat pencatatan, atau posisi tower crowdsourcing yang masih perkiraan. Tower layanan juga belum tentu tower terdekat; arah sektor, hambatan, dan pengaturan jaringan ikut berpengaruh.')
sub('Isi peta yang diperlukan')
p('Gunakan denah kampus dengan skala dan arah utara; beri penanda P1–P3, posisi tower, eNB ID, serta garis menuju tower layanan tiap titik. Arah garis dari tower ke titik ukur dapat disebut <b>arah layanan yang diperkirakan</b>; azimut antena yang sebenarnya memerlukan bukti tambahan. Peta belum dibuat karena lokasi kampus dan koordinat belum diberikan.')
page()

records=[
(1,'LTE B40 · 20 MHz · TDD · PCI 278',[
('Bukti spektral','Lebar terisi 18,20 MHz, konsisten dengan 100 RB (18 MHz aktif) pada kanal nominal 20 MHz.'),
('Bukti OFDM / waktu','T_u = 66,66 µs, spasi 15,00 kHz; puncak/median autokorelasi 38×. Daya on/off berulang tiap 5,0 ms; porsi pancaran downlink sekitar 75% pada rekaman.'),
('Bukti identitas','PSS 0,485; SSS 1,98×; N_ID_1 = 92, N_ID_2 = 2 → PCI 278. MIB lolos CRC 8/8: 100 RB, 20 MHz, 2 port, SFN 765–772.')],
'FDD tidak sesuai dengan pola jeda berkala serta hasil sinkronisasi TDD. NR 15 kHz bisa menyerupai OFDM LTE, tetapi dekode PBCH/MIB LTE yang lolos CRC menegaskan LTE.',
'Tinggi untuk teknologi, PCI, dan bandwidth. Angka 75% adalah estimasi selubung pada rekaman, bukan hasil dekode konfigurasi TDD lengkap.',
'2329,8 MHz → B40; EARFCN = 38650 + (2329,8 − 2300)/0,1 = <b>38948</b>.'),
(2,'Noise / spur instrumen · bukan LTE terverifikasi',[
('Bukti spektral','Tidak tampak blok OFDM lebar; terdapat garis sangat sempit sekitar MHz bulat, antara lain 2042, 2047, 2052, 2055, dan 2057 MHz.'),
('Bukti autokorelasi','Puncak/median hanya 2×. Kandidat lag 73,25 µs menghasilkan 13,65 kHz, tidak konsisten dengan sidik jari OFDM 15 kHz yang kuat.'),
('Bukti sinkronisasi','Pencarian LTE pada pusat rekaman tidak menemukan PSS di atas ambang 0,2; tidak ada identitas PCI atau MIB yang terverifikasi.')],
'Keluaran otomatis “LTE 1,4 MHz / FDD” tidak valid: algoritme tetap mengonversi lebar minimum 0,60 MHz menjadi RB dan menyebut sinyal kontinu sebagai FDD. Tidak adanya PSS saja tidak cukup, terlebih rekaman tidak dipusatkan; kesimpulan memakai gabungan bentuk spektrum dan autokorelasi.',
'Tinggi bahwa rekaman ini tidak menunjukkan LTE yang dapat dibuktikan; sedang untuk penyebab spesifik spur HackRF karena asal perangkat tidak bisa dipastikan dari IQ saja. Kanal, PCI, dan duplex tidak berlaku.',
'Pusat 2050,0 MHz berada di luar B1/B3/B8/B40 yang diminta. Tidak ada EARFCN LTE yang ditetapkan. Ini tidak berarti 2050 MHz berada di luar semua alokasi seluler di seluruh dunia.'),
(3,'LTE B3 · 20 MHz · FDD · PCI 54, 202, 419',[
('Bukti spektral / OFDM','Lebar terisi terukur 18,96 MHz; MIB menetapkan kanal 20 MHz (100 RB). T_u = 66,66 µs; spasi 15,00 kHz; puncak/median 40×.'),
('Bukti duplex','Pancaran kontinu pada selubung dan sinkronisasi SSS mode FDD saling mendukung. Pada pembacaan awal, PCI 54 dan 202 terdeteksi.'),
('Bukti identitas tambahan','Ambang PSS diturunkan dari 0,2 ke 0,1 untuk menguji sel lemah. PCI 419 ditemukan dengan skor 0,166; validitasnya didukung MIB lolos 8/8 (7 hasil melalui gabungan 40 ms). Ketiga sel: 20 MHz, 2 port.')],
'Noise tidak menghasilkan puncak OFDM kuat sekaligus CRC MIB yang valid. TDD tidak didukung oleh selubung dan hasil SSS. PCI berlainan di frekuensi sama adalah beberapa sel co-channel, bukan tiga kanal frekuensi yang harus dijumlahkan.',
'Tinggi untuk ketiga PCI karena MIB terverifikasi. PCI 419 lebih lemah dan memerlukan ambang sensitif; deteksi ini tidak menyatakan hanya tiga sel yang mungkin ada.',
'1870,0 MHz → B3; EARFCN = 1200 + (1870 − 1805)/0,1 = <b>1850</b>.'),
(4,'GSM DCS 1800 · 200 kHz per carrier · FDD',[
('Bukti spektral','Alat GSM mendeteksi tujuh kandidat carrier sempit. Empat memiliki FCCH berulang: 1857,8; 1858,2; 1859,2; dan 1859,6 MHz, masing-masing 21 kejadian.'),
('Bukti waktu','Pada carrier BCCH terkuat 1858,2 MHz, FCCH berjarak 46,15/50,77 ms: 16 selang × 10 frame dan 4 selang × 11 frame. Frame terukur 4,615 ms, timeslot 576,9 µs.'),
('Bukti nada FCCH','Nada terukur +65,60 kHz terhadap pusat carrier; setelah memperhitungkan CFO sekitar −2,10 kHz, cocok dengan nada FCCH sekitar +67,7 kHz khas GSM.')],
'Label otomatis “LTE 3 MHz” dari bentuk_sinyal.py menggabungkan beberapa carrier sempit. T_u semu 109,99 µs / 9,09 kHz bukan bukti LTE. Pola 10/11 frame dan FCCH jauh lebih spesifik untuk GSM. TDMA adalah pembagian waktu akses, bukan berarti duplex TDD.',
'Tinggi untuk GSM dan kanal nominal 200 kHz. Tiga kandidat lain belum terkonfirmasi FCCH; tidak otomatis tiga BCCH tambahan. Identitas BSIC/Cell ID GSM tidak didekode.',
'1859,6 MHz berada dalam rentang downlink DCS 1800 (beririsan rentang B3 LTE). <b>EARFCN tidak berlaku untuk sinyal GSM</b>; gunakan ARFCN 784. BCCH terkuat 1858,2 MHz memiliki ARFCN 777.'),
(5,'LTE B8 · 10 MHz · FDD · PCI 16',[
('Bukti spektral','Lebar terisi 9,30 MHz, dekat 50 RB × 180 kHz = 9 MHz aktif; kanal nominal 10 MHz dikonfirmasi oleh MIB.'),
('Bukti OFDM / duplex','Lag 1024 sampel pada 15,36 Msps memberi T_u = 66,66 µs dan spasi 15,00 kHz. Puncak/median 21×; selubung kontinu konsisten dengan FDD.'),
('Bukti identitas','PSS 0,884; SSS 3,17×; N_ID_1 = 5, N_ID_2 = 1 → PCI 16. MIB CRC lolos 8/8: 50 RB, 10 MHz, 2 port, SFN 575–582.')],
'Noise dan spur tidak menjelaskan blok lebar, korelasi kuat, serta CRC PBCH valid sekaligus. TDD tidak didukung oleh selubung maupun hasil SSS. MIB LTE membedakannya dari dugaan NR 15 kHz.',
'Tinggi untuk LTE, PCI, bandwidth, dan duplex. PCI 16 yang sama dengan inventaris titik A tidak cukup untuk memastikan eNB ID atau tower yang sama.',
'945,2 MHz → B8; EARFCN = 3450 + (945,2 − 925)/0,1 = <b>3652</b>.')]
for n,title,evidence,reject,confidence,band in records:
    h(f'Kasus 2 · Rekaman {n}')
    p(title,'SubID')
    for label,text in evidence:p(f'<b>{label}.</b> {text}')
    graphic(OUT/(f'misteri_{n}_gsm.png' if n==4 else f'misteri_{n}_laporan.png'),
        'Grafik diolah dari berkas IQ rekaman ini. Daya bersifat relatif, bukan pengukuran RSRP terkalibrasi.' if n!=4 else 'Grafik gsm_fcch.py: carrier sempit, nada FCCH, dan pola waktu GSM pada rekaman 4.',width=485)
    p('<b>Yang menolak dugaan lain.</b> '+reject)
    p('<b>Keyakinan.</b> '+confidence)
    p('<b>Uji frekuensi (Amplop B).</b> '+band)
    if n==3:
        p('SFN PCI 54 = 660–667; PCI 202 dan 419 = 638–645. Selisih awal frame sekitar 0,547 ms kembali mendukung sekurangnya dua eNodeB. Angka SFN berbeda dari inventaris Kasus 1 karena rekamannya berbeda.','SmallID')
    page()
h('Metode, sumber, dan jejak hasil')
sub('Analisis yang dijalankan')
p('Semua berkas dibaca sebagai pasangan I/Q signed int8. Durasi nominal dari ukuran berkas cocok dengan metadata: rekaman 1–3 dan 5 selama 0,4 s; rekaman 4 selama 1 s. Alat praktikum membuang transien awal 10 ms, sehingga analisis LTE mencakup 390 ms. Analisis bentuk sinyal GSM dibatasi 500 ms, sedangkan gsm_fcch.py memakai sisa rekaman sekitar 990 ms.')
p('bentuk_sinyal.py dijalankan pada kelima berkas dengan sample rate masing-masing. cari_sel_lte.py dijalankan pada rekaman 1, 2, 3, dan 5, dengan --fc sesuai Amplop B. gsm_fcch.py dijalankan pada rekaman 4. Rekaman 3 diuji ulang dengan --ambang 0.1 untuk memeriksa sel lemah; hasil MIB digunakan sebagai verifikasi tambahan.')
sub('Ringkasan keluaran dekode LTE')
rows=[['Berkas / PCI','PSS','SSS rasio','MIB CRC','MHz / port']]
for n,name in [(1,'misteri_1'),(3,'misteri_3_sensitif'),(5,'misteri_5')]:
    for r in csv.DictReader(open(OUT/f'{name}_sel.csv')):
        rows.append([f"{n} / {r['pci']}",r['skor_pss'],r['sss_rasio']+'×',r['mib_lolos']+'/'+r['mib_frame'],r['bw_mhz']+' / '+r['port']])
table(rows,[110,75,95,105,110])
sub('Referensi lokal yang digunakan')
p('1. kasus_detektif_seluler.html: soal Kasus 1–2, inventaris sel, petunjuk frekuensi, dan format laporan.<br/>2. praktikum_seluler/data/misteri/misteri.csv serta misteri_1.cs8 sampai misteri_5.cs8: bukti primer Kasus 2.<br/>3. praktikum_seluler/contoh_hasil/lokasi_A/survei_inventaris.csv dan survei_catatan.txt: angka timing/SFN dan penjelasan jam untuk Kasus 1.<br/>4. bentuk_sinyal.py, cari_sel_lte.py, gsm_fcch.py, seluler_dasar.py, serta lte_cell_search/lte_common.py: metode pemrosesan dan dekode broadcast.', 'SmallID')
p('Akar referensi: /home/astopoi/Downloads/untuk_mahasiswa/. Semua sumber dibaca tanpa diubah. Grafik dan angka Kasus 2 berasal dari pengolahan rekaman misteri, bukan penyalinan grafik contoh.','SmallID')
sub('Berkas pendamping')
p('Folder hasil/ menyimpan log analisis, tabel sel CSV, dan grafik lengkap. analisis.py menjalankan ulang analisis utama; buat_pdf.py membangkitkan grafik laporan dan PDF. Pengujian sensitif rekaman 3 memakai cari_sel_lte.py dengan parameter tambahan --ambang 0.1 dan awalan keluaran misteri_3_sensitif.','SmallID')

def footer(c,doc):
    w,h=doc.pagesize;c.saveState()
    c.setStrokeColor(colors.HexColor('#d6e0e8'));c.line(42,40,w-42,40)
    c.setFont('LS',8);c.setFillColor(colors.HexColor('#526777'))
    c.drawString(42,27,'DETEKTIF SELULER  /  KASUS 1 & 2')
    c.drawRightString(w-42,27,str(doc.page));c.restoreState()
doc=SimpleDocTemplate(str(HERE/'Jawaban_Kasus_1_dan_2_Detektif_Seluler.pdf'),pagesize=(595.28,841.89),rightMargin=50,leftMargin=50,topMargin=43,bottomMargin=53,title='Jawaban Kasus 1 dan 2 — Detektif Seluler',author='Laporan Analisis Praktikum')
doc.build(story,onFirstPage=footer,onLaterPages=footer)
print(doc.filename)
