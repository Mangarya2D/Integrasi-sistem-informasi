# ANALISIS PRAKTIKUM MINGGU 3
## Implementasi Sistem Legacy dan EAI (HTTP + XML)

### 1. Analisis Pola Arsitektur

Pada praktikum ini, pola yang digunakan adalah *Adapter Pattern* karena program Python (`adapter_service.py`) berfungsi sebagai penghubung antara sistem legacy dengan aplikasi yang ingin mengakses data mahasiswa. Sistem legacy menggunakan program C dan file `students_db.txt`, sedangkan adapter menyediakan akses melalui HTTP dengan format XML.

Dengan adanya adapter, data mahasiswa bisa diakses tanpa harus mengubah program C yang sudah dibuat sebelumnya. Klien cukup mengirimkan request ke alamat yang disediakan oleh adapter untuk melihat atau menambahkan data. Menurut saya, cara ini cukup membantu karena sistem lama tetap bisa digunakan tanpa harus membangun ulang seluruh sistem agar mendukung komunikasi melalui jaringan.

### 2. Analisis Overhead Serialisasi Data

Pada pengujian `GET /students/2415354001`, data mahasiswa ditampilkan dalam bentuk XML. Data yang diperoleh terdiri dari NIM, nama, jurusan, dan status.

#### A. Ukuran data asli

| Data | Jumlah karakter | Ukuran |
|---|---:|---:|
| NIM: `2415354001` | 10 | 10 byte |
| Nama: `I Made Sujana` | 13 | 13 byte |
| Jurusan: `Teknologi Informasi` | 19 | 19 byte |
| Status: `ACTIVE` | 6 | 6 byte |
| **Total** | **48** | **48 byte** |

Karena semua karakter pada data tersebut termasuk karakter ASCII, ukuran data aslinya adalah 48 byte jika menggunakan UTF-8.

#### B. Ukuran data dalam XML

Berikut contoh respons XML yang dihasilkan:

```xml
<?xml version='1.0' encoding='utf-8'?>
<StudentResponse><NIM>2415354001</NIM><Nama>I Made Sujana</Nama><Jurusan>Teknologi Informasi</Jurusan><Status>ACTIVE</Status></StudentResponse>
```

Jika dihitung berdasarkan contoh tersebut, ukuran seluruh respons XML adalah 182 byte, termasuk deklarasi XML dan baris baru setelah deklarasi.

#### C. Perhitungan overhead

Overhead dihitung dari selisih ukuran XML dengan ukuran data aslinya.

Overhead = 182 − 48 = **134 byte**

Persentase overhead:

\[
\frac{134}{48}\times100\%=279{,}17\%
\]

Dari hasil perhitungan tersebut, ukuran tambahan dari XML adalah 134 byte atau sekitar 279,17% dari ukuran data asli. Hal ini terjadi karena XML memiliki tag pembuka, tag penutup, dan deklarasi yang membuat data lebih terstruktur. Walaupun ukurannya menjadi lebih besar, XML memudahkan aplikasi lain membaca data karena formatnya memiliki susunan elemen yang jelas.

*Catatan: ukuran 182 byte berlaku jika hasil XML yang muncul sama persis dengan contoh di atas. Jika hasil pengujian berbeda, ukuran byte perlu disesuaikan.*

### 3. Prediksi Keterbatasan Integrasi

Jika terdapat 500 request POST yang masuk hampir bersamaan, server dan file `students_db.txt` bisa mengalami peningkatan beban kerja. Jika beberapa proses menulis ke file secara bersamaan tanpa pengaturan yang baik, data berisiko bertabrakan atau tidak tersimpan dengan benar. Kondisi ini dapat disebut sebagai Siklus Keruntuhan I/O Statis, yaitu keadaan ketika beban input/output yang tinggi membuat proses penyimpanan semakin sulit dikendalikan.

Namun, pada program yang digunakan dalam praktikum ini, `HTTPServer` standar Python menangani request secara berurutan dalam satu server. Jadi, 500 request tidak langsung menulis ke file secara bersamaan melalui server tersebut. Walaupun begitu, jika jumlah request terus meningkat, permintaan bisa menumpuk dan waktu respons menjadi lebih lama.

Salah satu solusi yang dapat digunakan adalah *Message Broker*. Dengan mekanisme antrean pesan, request yang masuk ditampung terlebih dahulu, kemudian diproses secara bertahap. Cara ini membantu mengatur proses penulisan data dan mengurangi risiko masalah ketika beban request meningkat.

### Kesimpulan

Berdasarkan praktikum yang dilakukan, sistem legacy berbasis C dapat dihubungkan dengan layanan HTTP menggunakan adapter Python dan format XML. Dengan cara ini, data mahasiswa bisa diakses melalui request GET dan ditambahkan melalui request POST tanpa perlu mengubah kode utama program C.

Penggunaan XML membuat struktur data lebih mudah dibaca, tetapi ukuran respons menjadi lebih besar dibandingkan data aslinya. Selain itu, sistem juga memiliki keterbatasan jika menerima banyak request dalam waktu singkat. Oleh karena itu, pengaturan proses penulisan data dan penggunaan antrean pesan dapat menjadi solusi jika sistem dikembangkan untuk menangani jumlah permintaan yang lebih besar.