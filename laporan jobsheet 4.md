Laporan Praktikum Pertemuan 4
Integrasi Sistem Informasi — Integrasi Modern Web Services & API Gateway (RESTful HTTP/JSON)
## Bagian A: Tabel Hasil Pengujian Benchmark

Hasil dari menjalankan `benchmark_serialization.py`:

| Jumlah Rekaman | JSON (Bytes) | XML (Bytes) | Reduksi Ukuran JSON (%) |
|---:|---:|---:|---:|
| 10 Data | 1.195 | 1.506 | 20,65% |
| 50 Data | 5.935 | 7.206 | 17,64% |
| 100 Data | 11.860 | 14.331 | 17,24% |
| 500 Data | 59.260 | 71.331 | 16,92% |

Berdasarkan hasil benchmark, JSON menghasilkan ukuran payload yang lebih kecil dibandingkan XML pada seluruh jumlah rekaman yang diuji. Reduksi ukuran JSON berada pada kisaran **16,92%–20,65%** dibandingkan XML.


Bagian B: Analisis Pertanyaan Kritis
1. Analisis Struktur Payload
Beberapa faktor sintaksis yang menyebabkan XML memiliki ukuran lebih besar daripada JSON untuk data yang sama adalah:
- Tag pembuka dan penutup: XML menuliskan nama field pada tag pembuka dan penutup, misalnya <nama>Budi</nama>. Pada JSON, nama field cukup ditulis sekali, misalnya "nama":"Budi".
- Pembungkus setiap rekaman: XML menggunakan elemen seperti <student>...</student>, sedangkan JSON menggunakan kurung kurawal untuk objek dan tanda kurung siku untuk array.
- Pengulangan nama field: Setiap rekaman memiliki empat field. Dalam XML, setiap field membutuhkan tag pembuka dan penutup sehingga nama field ditulis berulang kali.
- Karakter markup tambahan: XML menggunakan karakter seperti <, >, dan / untuk membentuk tag. JSON menggunakan struktur yang relatif lebih ringkas, seperti {}, [], titik dua, dan koma.
Akibatnya, payload XML menjadi lebih besar daripada JSON. Semakin banyak rekaman yang diserialisasi, semakin besar pula selisih ukuran total kedua format tersebut. Pada benchmark ini, JSON konsisten menghasilkan ukuran data yang lebih kecil.
2. Analisis Deserialisasi / Parsing di Sisi Klien
Ketika server mengirimkan respons dalam format JSON, aplikasi front-end JavaScript dapat memprosesnya menggunakan response.json() atau JSON.parse(). Hasilnya berupa objek dan array JavaScript yang dapat langsung diakses, misalnya melalui data.data[0].nama.

Sementara itu, pemrosesan XML biasanya memerlukan beberapa langkah tambahan:
1. Mengubah teks XML menjadi struktur DOM menggunakan DOMParser.
2. Menelusuri elemen yang diperlukan, misalnya dengan getElementsByTagName atau XPath.
3. Mengambil isi elemen menggunakan textContent.
4. Memetakan data secara manual ke objek JavaScript jika aplikasi membutuhkan struktur objek dan array.
Nilai XML yang diambil sebagai teks juga perlu dikonversi secara eksplisit apabila aplikasi membutuhkan tipe data seperti angka atau boolean.

Alasan JSON banyak digunakan dalam web services modern antara lain:
- Parsing lebih sederhana: JavaScript memiliki dukungan bawaan untuk JSON.
- Ukuran payload lebih kecil: Hasil benchmark menunjukkan JSON lebih hemat ukuran dibandingkan XML pada seluruh jumlah data yang diuji.
- Struktur data mudah digunakan: Objek dan array JSON cocok dengan struktur data yang umum digunakan di berbagai bahasa pemrograman.
- Dukungan ekosistem luas: JSON didukung oleh berbagai framework dan alat pengujian API, termasuk Flask, Postman, dan curl.
Dengan demikian, JSON menjadi pilihan yang praktis untuk pertukaran data melalui REST API, terutama ketika efisiensi payload dan kemudahan pengolahan data menjadi pertimbangan.
3. Bottleneck Arsitektur RESTful Synchronous
Apabila sistem legacy membutuhkan waktu 1,5 detik untuk melakukan file locking dan menulis data ke data.txt, proses penulisan dapat menjadi bottleneck ketika banyak klien mengirim permintaan POST secara bersamaan.

Sebagai ilustrasi, jika 100 permintaan harus diproses secara berurutan dan setiap penulisan membutuhkan 1,5 detik, waktu penyelesaian seluruh permintaan dapat mencapai:
\[
100 \times 1{,}5 = 150 \text{ detik}
\]

Artinya, klien yang diproses terakhir dapat menunggu hingga sekitar 150 detik, dengan asumsi setiap permintaan benar-benar diproses satu per satu tanpa overhead tambahan.

Dalam arsitektur RESTful yang sinkron, klien menunggu respons hingga proses di server selesai. Kondisi tersebut dapat menimbulkan beberapa masalah:
- Resource exhaustion: Koneksi dan thread server dapat tertahan terlalu lama sehingga sumber daya server berisiko habis.
- Request timeout: Klien dapat mengalami timeout apabila waktu tunggu melebihi batas yang ditentukan.
- Peningkatan latensi: Permintaan membutuhkan waktu lebih lama untuk mendapatkan respons.
- Dampak terhadap endpoint lain: Endpoint GET juga dapat melambat jika menggunakan worker atau sumber daya server yang sama.
Bagaimana gRPC dan Message Broker mengatasi masalah tersebut?
a. gRPC dengan HTTP/2

gRPC menggunakan HTTP/2 yang mendukung multiplexing, yaitu pengiriman beberapa stream permintaan dan respons melalui satu koneksi TCP. Hal ini mengurangi head-of-line blocking pada tingkat HTTP dibandingkan HTTP/1.1 yang menggunakan satu koneksi untuk beberapa permintaan berurutan.

Selain itu, gRPC umumnya menggunakan Protocol Buffers (Protobuf) sebagai format serialisasi biner yang ringkas. gRPC juga mendukung streaming dan deadline untuk mengatur batas waktu pemanggilan.

Namun, gRPC tidak otomatis menghilangkan waktu tunggu pada operasi sinkron. Jika klien melakukan pemanggilan unary dan server harus menunggu penulisan ke sistem legacy selesai, klien tetap menunggu respons. Dengan demikian, gRPC dapat meningkatkan efisiensi komunikasi, tetapi belum tentu mengatasi bottleneck pemrosesan di sistem legacy.

b. Asynchronous Message Broker

Message broker, seperti RabbitMQ atau Apache Kafka, memungkinkan gateway menerima permintaan dan memasukkan pesan ke antrean tanpa harus menunggu proses penulisan ke sistem legacy selesai.

Alur prosesnya adalah sebagai berikut:
1. Klien mengirim permintaan POST ke API Gateway.
2. Gateway memvalidasi data dan memasukkan pesan ke antrean.
3. Gateway mengembalikan respons 202 Accepted untuk menyatakan bahwa permintaan telah diterima untuk diproses.
4. Worker atau consumer mengambil pesan dari antrean dan menuliskannya ke sistem legacy sesuai kapasitas pemrosesan.
5. Jika terjadi kegagalan, mekanisme retry dan penanganan pesan gagal dapat diterapkan sesuai konfigurasi sistem.
Pendekatan ini memberikan beberapa keuntungan:
- Klien tidak perlu menunggu seluruh proses penulisan ke sistem legacy selesai.
- Lonjakan permintaan dapat ditampung oleh antrean.
- Kecepatan pemrosesan dapat disesuaikan dengan kapasitas sistem legacy.
- Gateway dan sistem legacy tidak lagi harus berkomunikasi secara langsung untuk menyelesaikan setiap permintaan.
- Pesan dapat diproses ulang jika terjadi kegagalan, bergantung pada konfigurasi broker dan mekanisme pemrosesan.
Meskipun demikian, 202 Accepted bukan berarti data sudah berhasil ditulis ke sistem legacy. Respons tersebut hanya menunjukkan bahwa permintaan telah diterima untuk diproses.
Kesimpulan
Berdasarkan praktikum integrasi sistem informasi pertemuan 4, API Gateway berbasis Flask dapat digunakan sebagai lapisan penghubung antara klien dan sistem legacy berbasis file data.txt melalui REST API dengan protokol HTTP dan format JSON.

Hasil benchmark menunjukkan bahwa JSON memiliki ukuran payload yang lebih kecil daripada XML untuk seluruh jumlah rekaman yang diuji. Efisiensi ukuran JSON berkisar antara 16,92% hingga 20,65%. Hal ini menunjukkan bahwa JSON merupakan format yang lebih ringkas untuk pertukaran data pada skenario pengujian ini.

Dari sisi arsitektur, komunikasi RESTful yang sinkron dapat menimbulkan bottleneck ketika sistem legacy memiliki waktu pemrosesan yang lambat. gRPC dengan HTTP/2 dapat meningkatkan efisiensi komunikasi, sedangkan asynchronous message broker dapat mengurangi waktu tunggu klien dengan memisahkan penerimaan permintaan dari pemrosesan ke sistem legacy.

Dengan demikian, pemilihan format serialisasi dan pola komunikasi perlu mempertimbangkan ukuran payload, kemudahan pemrosesan, kapasitas sistem legacy, dan kebutuhan respons aplikasi.
