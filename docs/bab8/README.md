# Praktikum 08 — Kotlin Coroutines & Flow

Proyek ini melanjutkan implementasi REST API dan pencarian Modul 07 di workspace yang sama.

## Implementasi

- Service Retrofit, remote data source, dan repository menggunakan suspend function.
- HomeViewModel dan DetailViewModel memakai viewModelScope dan StateFlow immutable untuk UI.
- ViewModel Home berada di package/direktori ui/home dan dibuat dengan ViewModelProvider.Factory.
- Home/Detail mengoleksi state melalui collectAsStateWithLifecycle.
- Pencarian otomatis: debounce 500 ms → trim → distinctUntilChanged → collectLatest.
- Query kosong memuat 10 profil awal; retry dan Refresh mengikuti query aktif.
- Request sebelumnya dibatalkan, CancellationException diteruskan.
- Navigasi Home, Detail, Profile, About dan back stack dipertahankan.

## Validasi 13 November 2026

Perintah `./gradlew assembleDebug testDebugUnitTest lintDebug --console=plain` berhasil.
Tiga unit test HomeViewModel menguji debounce/query kosong/duplikat, retry/refresh, serta cancellation.
Lint tidak menghasilkan error; peringatan dependency dan konfigurasi proyek masih tersedia pada laporan lint.

Pengujian HP fisik Samsung A32 (SM-A325F): data awal, search john, Detail John Doe ID 102,
Back ke Home, loading, error saat Wi-Fi/data dimatikan, Coba Lagi setelah koneksi pulih,
Refresh query john, Refresh query kosong, Profile dan About. Wi-Fi dan data seluler telah
kembali aktif sesuai kondisi awal. Screenshot aplikasi asli ada di screenshots/03–14.
Gambar 01–02 merupakan cuplikan source yang dirender dari file Kotlin, bukan tangkapan editor Android Studio.

## Luaran

- Laporan DOCX di root proyek, cover mengikuti laporan BAB 7; revisi hanya membahas 10 ketentuan Tugas Praktikum (Refresh), dengan 2 halaman isi di luar cover.
- Salinan PDF laporan di direktori ini, sudah diperiksa hasil render dan jumlah halamannya.
- APK: app/build/outputs/apk/debug/app-debug.apk (sudah terpasang pada HP).
- Screenshot asli: screenshots/.
- logcat.txt: log yang difilter hanya untuk aplikasi proyek.
- checkpoint-modul7.tar.gz: snapshot source dan konfigurasi sebelum refactoring;
  dibuat tanpa commit karena workspace memiliki perubahan Modul 07 yang belum di-commit.
- buat_laporan.py: generator laporan menggunakan cover/aset dari DOCX BAB 7.
