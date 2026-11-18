# Modul 09 — Latihan/Tugas Akhir Praktikum

Lingkup laporan mengikuti bagian 7 modul: FavoritesScreen beserta enam ketentuan minimumnya.
Room, DataStore, dan tombol favorit Detail ditambahkan sebagai prasyarat fitur tersebut pada proyek Modul 08.

## Implementasi

- `Routes.FAVORITES` dan tombol Favorites dari Home.
- `FavoriteStudentEntity`, `FavoriteStudentDao`, singleton `AppDatabase` (navigation_lab.db).
- `FavoriteRepository`/`RoomFavoriteRepository`: DAO tidak diakses UI; entity dipetakan ke Student.
- `FavoritesViewModel`: combine Flow Room dengan preferensi sortAscending, StateFlow read-only.
- `FavoritesScreen`: nama dan email, navigasi ke Detail berdasarkan ID, empty/loading/error state.
- `DetailViewModel`: simpan/hapus favorit melalui repository, status reaktif. Favorit tersimpan dapat dibuka offline.
- `DataStoreUserPreferencesRepository`: lastSearchQuery serta sortAscending (A–Z/Z–A).
- Home memulihkan query sebelum mengamati pencarian dan menyimpan perubahan dengan debounce.
- Coroutine tetap berada di ViewModel; Compose menggunakan collectAsStateWithLifecycle.

Anotasi modul diikuti: plugin KSP dipasang, extension DataStore internal, nama Student dipetakan ke
firstName dengan lastName kosong, repository diteruskan melalui factory dan host navigasi.
Kolom university ikut disimpan agar Detail lokal mempertahankan informasi profil.

## Pengujian otomatis

`./gradlew assembleDebug testDebugUnitTest lintDebug assembleDebugAndroidTest --console=plain`

- 7 unit test lulus (termasuk 1 test bawaan template): pencarian/cancellation/refresh,
  pemulihan query, daftar favorit reaktif, sorting, penghapusan, dan Detail favorit offline.
- 2 instrumented test LocalStorageTest lulus pada Samsung SM-A325F:
  Room persist setelah database ditutup/dibuka; Flow memancarkan penghapusan;
  DataStore persist setelah instance/scope dibuat ulang.
- Lint tanpa error; peringatan dependency/config/resource tetap tercantum di laporan lint.

Instrumented test memakai database/file preferensi khusus di direktori pengujian dan membersihkannya
setelah selesai; tidak menghapus database utama aplikasi.

## Artefak

- DOCX BAB 9 di root proyek; cover mengikuti BAB 7. Isi hanya latihan/tugas akhir.
- PDF BAB 9 di direktori ini.
- Screenshot asli HP di screenshots/; bukti persistensi menggunakan force-stop dan buka ulang aplikasi.
- Generator dokumen: buat_laporan.py.
- Skenario UI ADB: uji_hp.py (memerlukan Home awal dengan query kosong dan dua profil contoh belum favorit).
- Snapshot sebelum implementasi: checkpoint-modul8.tar.gz; workspace pengguna tidak di-reset/di-commit.
- Schema Room: app/schemas/com.example.bab6.data.local.AppDatabase/1.json.
