## Deskripsi

Buat fitur **Kalkulator Subnet**. Aplikasi menerima alamat IPv4 dan prefix,
lalu menghitung subnet mask, network address, broadcast address, range host,
dan jumlah host usable. Hasilnya harus bisa dinilai guru SMK TKJ tanpa membaca
kode, cukup lewat halaman web (penggaris alamat dan jejak biner IP AND mask).

Sumber kebenaran: `SPEC.md`, bagian 3 (Aturan Validasi),
4.1 (`hitung_subnet`), 5 (Kontrak API), 6 (Halaman Web), dan 7 (Tabel Test Case).
Desain UI: `index.html` dan `DESIGN.md`.

Fitur VLSM (`alokasi_vlsm`, `POST /api/vlsm`) **tidak** termasuk issue ini.
VLSM dikerjakan di issue terpisah.

## Tugas

- [ ] Tulis `test_main.py` (pytest + `pytest.mark.parametrize`) untuk semua kasus
      subnet dan API di SPEC.md §7.1, §7.2, dan §7.4 (A1–A4), **sebelum** implementasi.
- [ ] Jalankan `uv run pytest` dan pastikan test **merah** dulu.
- [ ] Implementasikan `hitung_subnet(ip: str, prefix: int) -> dict` di `main.py`:
  - [ ] Validasi IP: 4 oktet, 0–255, tanpa nol di depan, tanpa spasi. Input tidak valid → `ValueError`.
  - [ ] Validasi prefix: bilangan bulat 0–32.
  - [ ] Network = IP **AND** subnet mask (bitwise).
  - [ ] Aturan khusus: /31 (RFC 3021: 2 host, broadcast `None`) dan /32 (1 host, broadcast `None`).
- [ ] Endpoint `GET /` (menyajikan `index.html`) dan `GET /api/subnet?ip=&prefix=`.
      Semua kesalahan input → HTTP 400 dengan field `detail` (bukan 422).
- [ ] Hubungkan tab Subnet di `index.html` ke API dan pastikan halaman tampil
      (`uv run fastapi dev main.py`).
- [ ] Jangan mengubah test agar lulus.

## Kriteria Penerimaan

Semua kasus berikut dari SPEC.md §7 lulus di `uv run pytest`:

| Kelompok | Kasus | Ringkasan |
|---|---|---|
| Subnet valid (§7.1) | S1–S9 | Contoh: 172.16.5.130/25 → network .128, broadcast .255, 126 host; 192.168.1.0/31 → 2 host, broadcast `None`; 192.168.1.5/32 → 1 host |
| Input ditolak (§7.2) | E1–E10 | 256.1.1.1, 192.168.01.1, 192.168.1, abc, kosong, prefix 33, prefix -1, 5 oktet, spasi, oktet negatif → `ValueError` |
| API (§7.4) | A1–A4 | `GET /` → 200 HTML; `GET /api/subnet` sukses → 200; input tidak valid / prefix hilang → 400 + `detail` |

Selain itu:

- Halaman menampilkan hasil dan pesan error dari field `detail` (keadaan kosong, sukses, dan error).
- CI hijau di Pull Request.

## Alur Kerja

1. **Issue**: issue ini.
2. **Branch**: `feature/issue-<nomor>-subnet-calculator` dari `main`.
3. **Test dulu**: tulis `test_main.py`, jalankan, dan pastikan merah. Commit `test: tulis test subnet lebih dulu`.
4. **Implementasi**: kerjakan `main.py` sampai semua test hijau. Commit `feat: implementasi hitung_subnet dan API`.
5. **Commit**: commit kecil dengan pesan Conventional Commits.
6. **Pull Request** ke `main`. Deskripsi memuat `Closes #<nomor>`.
7. **CI**: pipeline `SQA Pipeline` harus hijau.
8. **Merge** setelah CI hijau.
