# DESIGN.md — Kalkulator Subnet & VLSM

Diturunkan dari `index.html` yang sudah dibangun. Brief mengikat: light mode,
bersih, gaya mirip Google, latar putih, aksen biru, kartu membulat.

## Gagasan inti

**Penggaris ruang alamat.** Setiap blok alamat digambar sebagai pita horizontal
yang lebarnya sebanding persis dengan jumlah alamat. Mode Subnet menandai letak
IP di antara network dan broadcast. Mode VLSM menunjukkan cara blok induk
terbagi beserta sisa ruangnya. Penggaris didampingi **jejak biner** (IP AND
mask = network) sehingga guru bisa memverifikasi tanpa membaca kode.

## Token warna

| Token | Nilai | Peran |
|---|---|---|
| `--bg` | #ffffff | Latar halaman dan kartu |
| `--surface` / `--surface-2` | #f8f9fa / #f1f3f4 | Panel biner, header tabel, pita penggaris |
| `--line` / `--line-soft` | #dadce0 / #e8eaed | Hairline, pemisah sel |
| `--text` / `--text-2` / `--text-3` | #202124 / #5f6368 / #70757a | Teks utama, label, placeholder |
| `--blue` / `--blue-strong` / `--blue-ink` / `--blue-tint` | #1a73e8 / #1765cc / #174ea6 / #e8f0fe | Aksi utama, tab aktif, bit network, rentang host |
| `--red` / `--red-tint` | #d93025 / #fce8e6 | Error, garis batas prefix |
| `--host` | #70757a | Bit host |
| `--seg-1..6` (+ `-ink`, `-edge`) | biru, hijau, amber, ungu, teal, merah (tint) | Segmen VLSM, berulang setiap 6 subnet |

Strategi warna: Restrained. Biru hanya untuk aksi, status terpilih, dan bit
network; warna segmen hanya dipakai di penggaris VLSM dan swatch tabel.

## Tipografi

- UI: `"Google Sans Text", Roboto, system-ui, sans-serif`.
- Data (IP, mask, bit, CIDR): `"Roboto Mono", ui-monospace`, dengan `tabular-nums`.
- Skala: h1 1.75rem (mobile 1.375rem); judul hasil 1.375rem; nilai hasil
  clamp(1.125rem → 1.5rem); label 0.8125rem; body 1rem.

## Bentuk dan komponen

- Radius: kartu 16px, kontrol 8px, tombol pill (26px).
- Kontrol input tinggi 52px, fokus = border biru + ring 1px; error = merah + `aria-invalid`.
- Tab: garis bawah biru 3px, navigasi dengan panah kiri/kanan.
- Grid nilai: 3 kolom → 2 kolom (≤720px) → 1 kolom (≤400px), dipisah hairline.
- Tabel biner: bit network biru tebal, bit host abu, garis merah di batas
  prefix, garis tebal sebelum baris hasil. Di mobile, bit dipindah ke baris sendiri.
- Tabel alokasi VLSM: tabel di desktop, kartu label/nilai di mobile.
- Penggaris: tick 1/8 blok (lebih sedikit bila blok < 8 alamat). Segmen yang
  labelnya tidak muat hanya menampilkan nomor subnet. Sisa ruang VLSM ditandai arsir.

## Keadaan

Kosong (petunjuk + contoh soal yang bisa diklik), memuat (tombol "Menghitung…"
dinonaktifkan), sukses, error (pesan `detail` di bawah form, field ditandai).

## Gerak

Satu momen: segmen penggaris tumbuh dari kiri (450ms, ease-out eksponensial),
hasil muncul dengan fade 220ms. Semua dimatikan saat `prefers-reduced-motion`.
