# SPEC.md — Kalkulator Subnet & VLSM

Versi 1.0 · 2026-11-03

## 1. Tujuan

Guru SMK TKJ butuh alat untuk memeriksa hitungan subnetting dan VLSM.
Hasil alat ini harus bisa dicocokkan dengan hitungan manual, tanpa
membaca kode.

Yang dibangun adalah aplikasi web satu halaman:

- Backend: Python 3.12 + FastAPI, dikelola dengan `uv`.
- Logika perhitungan ada di `main.py`.
- Test ada di `test_main.py` (pytest).
- Antarmuka: satu file `index.html` dengan dua mode, yaitu Subnet dan VLSM.

Kriteria keberhasilan:

1. Semua kasus di Tabel Test Case (bagian 7) lulus di `uv run pytest`.
2. Network address dihitung dengan bitwise AND antara IP dan subnet mask,
   sehingga sesuai teori yang diajarkan di kelas.
3. Setiap input tidak valid ditolak dengan pesan yang jelas. Fungsi
   melempar `ValueError` dan API mengembalikan HTTP 400 dengan field
   `detail`. Tidak boleh ada error 500.
4. Guru bisa memverifikasi hasil hanya dari tampilan halaman web.

## 2. Pengguna

- **Guru TKJ**: membuat soal subnetting dan VLSM, lalu memeriksa kunci
  jawabannya.
- **Siswa TKJ** (sekunder): mengecek hasil latihan sendiri.

## 3. Aturan Validasi

### 3.1 Alamat IPv4 (`ip`)

| Aturan | Contoh ditolak |
|---|---|
| Tepat 4 oktet, dipisah titik | `192.168.1`, `1.2.3.4.5` |
| Tiap oktet hanya berisi digit 0-9 | `abc`, `192.168.-1.1`, `1.2.3.a` |
| Nilai tiap oktet 0-255 | `256.1.1.1` |
| Tidak ada nol di depan (kecuali oktet `0` itu sendiri) | `192.168.01.1`, `010.0.0.1` |
| Tidak ada spasi di mana pun, termasuk di awal atau akhir; tidak di-trim | `" 192.168.1.1"`, `192.168. 1.1` |
| Tidak boleh kosong | `""` |

Keputusan tambahan:

- IP yang sama dengan network address atau broadcast address subnetnya
  **diterima** dan dihitung seperti biasa. Contoh: `192.168.1.0/24` dan
  `192.168.1.255/24`.
- Alamat khusus seperti `127.x`, `224.x`, dan `0.0.0.0` **diterima** dan
  dihitung tanpa peringatan.

### 3.2 Prefix (`prefix`)

- Harus bilangan bulat dari 0 sampai 32.
- Ditolak: `33`, `-1`, `24.5`, `abc`, dan nilai kosong.
- Notasi mask desimal seperti `255.255.255.0` **tidak didukung** sebagai
  prefix.

### 3.3 Input VLSM

- `network_cidr` berformat `a.b.c.d/p`. IP dan prefix-nya mengikuti
  aturan 3.1 dan 3.2.
- `network_cidr` harus berupa **alamat jaringan** (IP AND mask = IP).
  Contoh: `192.168.1.5/24` ditolak dan tidak dinormalisasi otomatis.
- `kebutuhan_host` berupa list bilangan bulat. List kosong ditolak, dan
  setiap nilai < 1 ditolak.

## 4. Kontrak Fungsi

### 4.1 `hitung_subnet(ip: str, prefix: int) -> dict`

Fungsi ini mengembalikan dict dengan kunci berikut:

| Kunci | Tipe | Keterangan |
|---|---|---|
| `mask` | str | Subnet mask dalam notasi desimal bertitik |
| `network` | str | `ip AND mask` (bitwise) |
| `broadcast` | str atau None | `network OR (NOT mask)`; bernilai `None` untuk /31 dan /32 |
| `first_host` | str | Host pertama yang bisa dipakai |
| `last_host` | str | Host terakhir yang bisa dipakai |
| `usable_hosts` | int | Jumlah host yang bisa dipakai |

Aturan per prefix:

| Prefix | usable_hosts | first_host | last_host | broadcast |
|---|---|---|---|---|
| 0-30 | 2^(32-prefix) − 2 | network + 1 | broadcast − 1 | network OR wildcard |
| 31 (RFC 3021, point-to-point) | 2 | network | network + 1 | `None` |
| 32 (host route) | 1 | ip | ip | `None` |

Jika input tidak valid, fungsi melempar `ValueError` dengan pesan
berbahasa Indonesia, misalnya "Oktet harus 0-255".

### 4.2 `alokasi_vlsm(network_cidr: str, kebutuhan_host: list[int]) -> list[dict]`

Algoritma:

1. Validasi input sesuai aturan 3.3.
2. Urutkan kebutuhan dari yang **terbesar** ke yang terkecil. Jika ada
   nilai yang sama, urutan aslinya dipertahankan (sort stabil).
3. Untuk tiap kebutuhan `n`, ukuran blok adalah pangkat 2 terkecil yang
   ≥ `n + 2`, dengan ukuran minimal 4 alamat (/30). Prefix blok =
   32 − log2(ukuran).
4. Alokasikan blok berurutan mulai dari alamat network. Blok berikutnya
   dimulai tepat setelah broadcast blok sebelumnya.
5. Jika ada blok yang melewati batas broadcast `network_cidr`, lempar
   `ValueError` ("Blok tidak cukup").

Setiap elemen hasil berisi `kebutuhan` (int), `network_cidr` (str), dan
semua kunci `hitung_subnet` untuk blok tersebut. Urutan hasil mengikuti
**urutan alokasi**, bukan urutan input.

## 5. Kontrak API

| Metode | Path | Input | Sukses | Gagal |
|---|---|---|---|---|
| GET | `/` | — | 200, isi `index.html` | — |
| GET | `/api/subnet` | query `ip`, `prefix` | 200, JSON hasil `hitung_subnet` | 400 `{"detail": "<pesan>"}` |
| POST | `/api/vlsm` | JSON `{"network": "192.168.1.0/24", "kebutuhan_host": [100, 50]}` | 200, JSON list hasil `alokasi_vlsm` | 400 `{"detail": "<pesan>"}` |

Ketentuan tambahan:

- Semua kesalahan input, termasuk parameter yang hilang atau bertipe
  salah, dikembalikan sebagai **HTTP 400** dengan field `detail`, bukan
  422.
- `broadcast` bernilai `None` dikirim sebagai `null` di JSON.

## 6. Halaman Web

- Satu halaman `index.html` dengan dua tab: **Subnet** dan **VLSM**.
- **Tab Subnet** berisi:
  - field IP dan field prefix (0-32),
  - tombol "Hitung",
  - kartu hasil berisi mask, network, broadcast (tampil "— (point-to-point)"
    untuk /31 dan "—" untuk /32), first host, last host, dan usable hosts.
- **Tab VLSM** berisi:
  - field network CIDR,
  - daftar kebutuhan host yang bisa ditambah dan dihapus,
  - tabel hasil dengan kolom kebutuhan, network/CIDR, mask, range host,
    broadcast, dan usable hosts.
- **Tiga keadaan**:
  - kosong: belum ada hasil,
  - sukses: hasil tampil,
  - error: pesan dari field `detail` tampil di bawah form.
- Halaman memanggil API memakai `fetch`. Tidak ada perhitungan subnet di
  JavaScript.

## 7. Tabel Test Case

### 7.1 `hitung_subnet`: kasus valid

| # | Input | mask | network | broadcast | first_host | last_host | usable_hosts |
|---|---|---|---|---|---|---|---|
| S1 | 172.16.5.130/25 | 255.255.255.128 | 172.16.5.128 | 172.16.5.255 | 172.16.5.129 | 172.16.5.254 | 126 |
| S2 | 10.0.0.0/30 | 255.255.255.252 | 10.0.0.0 | 10.0.0.3 | 10.0.0.1 | 10.0.0.2 | 2 |
| S3 | 192.168.1.0/31 | 255.255.255.254 | 192.168.1.0 | None | 192.168.1.0 | 192.168.1.1 | 2 |
| S4 | 192.168.1.5/32 | 255.255.255.255 | 192.168.1.5 | None | 192.168.1.5 | 192.168.1.5 | 1 |
| S5 | 192.168.1.10/24 | 255.255.255.0 | 192.168.1.0 | 192.168.1.255 | 192.168.1.1 | 192.168.1.254 | 254 |
| S6 | 10.10.10.10/20 | 255.255.240.0 | 10.10.0.0 | 10.10.15.255 | 10.10.0.1 | 10.10.15.254 | 4094 |
| S7 | 10.1.2.3/8 | 255.0.0.0 | 10.0.0.0 | 10.255.255.255 | 10.0.0.1 | 10.255.255.254 | 16777214 |
| S8 | 0.0.0.0/0 | 0.0.0.0 | 0.0.0.0 | 255.255.255.255 | 0.0.0.1 | 255.255.255.254 | 4294967294 |
| S9 | 192.168.1.255/24 | 255.255.255.0 | 192.168.1.0 | 192.168.1.255 | 192.168.1.1 | 192.168.1.254 | 254 |

### 7.2 `hitung_subnet`: kasus ditolak (`ValueError` / HTTP 400)

| # | ip | prefix | Alasan |
|---|---|---|---|
| E1 | 256.1.1.1 | 24 | Oktet > 255 |
| E2 | 192.168.01.1 | 24 | Ada nol di depan |
| E3 | 192.168.1 | 24 | Hanya 3 oktet |
| E4 | abc | 24 | Bukan angka |
| E5 | "" (kosong) | 24 | Kosong |
| E6 | 192.168.1.1 | 33 | Prefix > 32 |
| E7 | 192.168.1.1 | -1 | Prefix < 0 |
| E8 | 1.2.3.4.5 | 24 | Ada 5 oktet |
| E9 | " 192.168.1.1" | 24 | Ada spasi |
| E10 | 192.168.-1.1 | 24 | Oktet negatif |

### 7.3 `alokasi_vlsm`

| # | Input | Hasil yang diharapkan (network_cidr → broadcast, usable_hosts) |
|---|---|---|
| V1 | 192.168.1.0/24, [100, 50, 20, 2] | 192.168.1.0/25 → .127, 126 · 192.168.1.128/26 → .191, 62 · 192.168.1.192/27 → .223, 30 · 192.168.1.224/30 → .227, 2 |
| V2 | 192.168.1.0/24, [2, 20, 100, 50] | Sama dengan V1 (diurutkan lebih dulu) |
| V3 | 192.168.1.0/24, [126, 126] | 192.168.1.0/25 · 192.168.1.128/25 |
| V4 | 192.168.1.0/24, [62] | 192.168.1.0/26 |
| V5 | 192.168.1.0/24, [63] | 192.168.1.0/25 |
| V6 | 192.168.1.0/24, [1] | 192.168.1.0/30 (blok minimal) |
| V7 | 192.168.1.0/24, [200, 100] | Ditolak: tidak muat |
| V8 | 192.168.1.0/24, [] | Ditolak: daftar kosong |
| V9 | 192.168.1.0/24, [0] atau [-5] | Ditolak: kebutuhan < 1 |
| V10 | 192.168.1.5/24, [10] | Ditolak: bukan alamat jaringan |
| V11 | 192.168.1.0/33, [10] | Ditolak: prefix tidak valid |

### 7.4 API

| # | Permintaan | Hasil yang diharapkan |
|---|---|---|
| A1 | `GET /` | 200, berisi HTML |
| A2 | `GET /api/subnet?ip=172.16.5.130&prefix=25` | 200, sama dengan S1 |
| A3 | `GET /api/subnet?ip=256.1.1.1&prefix=24` | 400, ada field `detail` |
| A4 | `GET /api/subnet?ip=192.168.1.1` (tanpa prefix) | 400, ada field `detail` |
| A5 | `POST /api/vlsm` dengan V1 | 200, network_cidr sama dengan V1 |
| A6 | `POST /api/vlsm` dengan V7 | 400, ada field `detail` |

## 8. Di Luar Cakupan

- IPv6.
- Input berupa notasi mask desimal atau wildcard mask.
- Supernetting / route summarization.
- Login, penyimpanan riwayat, dan database.
- Peringatan untuk alamat khusus (loopback, multicast, private/public).
- Normalisasi otomatis untuk input yang tidak valid, misalnya trim spasi
  atau membetulkan alamat jaringan.
- Strategi VLSM selain "terbesar dulu, berurutan", misalnya best-fit.
