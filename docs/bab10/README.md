# Modul 10 — Latihan/Tugas Praktikum

Laporan membahas hanya lima ketentuan bagian 7 modul: label Precise/Approximate,
accuracy dan waktu pembaruan, Perbarui Lokasi, pesan penolakan dan Minta Izin Lagi,
serta stabilitas pada Approximate/lokasi tidak tersedia. Fitur lokasi dasar ditambahkan
sebagai prasyarat latihan pada proyek Modul 09.

## Implementasi

- data/location: DeviceLocation, LocationAccess, LocationRepository, DefaultLocationRepository.
- ui/location: LocationUiState, LocationViewModel, LocationScreen.
- Route location dan tombol Buka Lokasi dari Home; dependency dibuat sekali di host navigasi.
- Manifest hanya COARSE/FINE foreground location; tidak ada background location.
- UI menggunakan Activity Result API dan memeriksa ulang izin ketika ON_RESUME dan setiap klik.
- StateFlow private/read-only; pengambilan data berjalan melalui viewModelScope dan repository.
- COARSE saja diterima, priority BALANCED_POWER_ACCURACY; FINE memakai HIGH_ACCURACY.
- getCurrentLocation satu kali dengan timeout 20 detik, cancellation token dibatalkan di finally.
- Tidak ada maps, geocoding, continuous tracking, atau foreground service.
- Waktu adalah waktu request terakhir yang berhasil; hasil gagal tidak menggantinya.
- Hasil Precise lama dibersihkan ketika status izin berubah.

## Verifikasi

Build, unit test, dan lint: lihat validasi.txt. Enam test baru menguji permission denied
tanpa request, pemetaan izin, keberhasilan Approximate, pembaruan timestamp, error/retry,
serta pembatalan ketika izin berubah atau layar tidak aktif. Tujuh test modul sebelumnya
juga tetap lulus. Lint tidak menemukan error; peringatan konfigurasi/resource/dependency
bawaan proyek tetap ada pada laporan lint.

Semua skenario UI lulus, termasuk Precise, Approximate, Perbarui Lokasi, denied/izin ulang, lokasi nonaktif dan retry.
Screenshot diambil langsung dari HP Samsung SM-A325F. File asli tersedia di screenshots/.
Tidak ada koordinat simulasi yang disuntikkan. Skenario uji menggunakan izin runtime aplikasi
praktikum dan mematikan layanan Lokasi sementara; layanan dipulihkan dalam finally.

## Laporan

DOCX berada di root proyek; PDF dan generator berada di direktori ini.
Format mengikuti BAB 7–9: cover identitas yang sama, poin tugas bernomor, nama file,
serta potongan kode editable Courier New 9 pt dengan latar abu-abu F2F2F2 dan indentasi utuh.
Snapshot kode sebelum perubahan ada di checkpoint-modul9.tar.gz; perubahan pengguna tidak di-reset.

## Referensi implementasi

- Modul Praktikum 10 - Location Services dan Permission FILKOM UB.pdf (lokal).
- https://developers.google.com/android/reference/com/google/android/gms/location/FusedLocationProviderClient
- https://kotlinlang.org/api/kotlinx.coroutines/kotlinx-coroutines-play-services/kotlinx.coroutines.tasks/await.html

Catatan pengujian perangkat: pada Samsung, pengubahan location_mode melalui command ADB tidak
langsung mencerminkan master switch LocationManager. Pengujian off akhirnya menggunakan
sakelar Settings serta menutup dialog informasi "No location access". Status layanan diperiksa
false sebelum screenshot error, lalu dipulihkan true. Penolakan permanen Android ditangani
UI dengan Buka Pengaturan; hanya flag penolakan aplikasi lab yang direset saat menguji ulang dialog.
