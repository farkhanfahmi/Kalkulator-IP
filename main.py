"""Kalkulator Subnet & VLSM — backend FastAPI. Kontrak lengkap ada di SPEC.md."""

import re
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import FileResponse, JSONResponse

app = FastAPI(title="Kalkulator Subnet & VLSM")

INDEX_HTML = Path(__file__).parent / "index.html"

# Satu oktet: "0" atau 1-3 digit ASCII tanpa nol di depan (nilai 0-255 dicek terpisah).
_POLA_OKTET = re.compile(r"0|[1-9][0-9]{0,2}")


# ---------------------------------------------------------------------------
# Konversi alamat
# ---------------------------------------------------------------------------
def _ip_ke_int(ip: str) -> int:
    """Ubah IPv4 desimal bertitik menjadi bilangan 32-bit. Raise ValueError bila tidak valid."""
    if not isinstance(ip, str) or ip == "":
        raise ValueError("Alamat IP tidak boleh kosong.")
    oktet = ip.split(".")
    if len(oktet) != 4:
        raise ValueError("Alamat IP harus terdiri dari tepat 4 oktet, misalnya 192.168.1.10.")
    nilai = 0
    for o in oktet:
        if not _POLA_OKTET.fullmatch(o):
            raise ValueError(
                f"Oktet '{o}' tidak valid: hanya angka 0-255, tanpa spasi dan tanpa nol di depan."
            )
        angka = int(o)
        if angka > 255:
            raise ValueError(f"Oktet {angka} di luar rentang: setiap oktet harus 0-255.")
        nilai = (nilai << 8) | angka
    return nilai


def _int_ke_ip(nilai: int) -> str:
    """Ubah bilangan 32-bit menjadi IPv4 desimal bertitik."""
    return ".".join(str((nilai >> geser) & 0xFF) for geser in (24, 16, 8, 0))


def _cek_prefix(prefix: int) -> int:
    # bool adalah turunan int di Python; True/False bukan prefix yang sah.
    if isinstance(prefix, bool) or not isinstance(prefix, int):
        raise ValueError("Prefix harus bilangan bulat 0-32.")
    if not 0 <= prefix <= 32:
        raise ValueError(f"Prefix {prefix} di luar rentang: prefix harus 0-32.")
    return prefix


# ---------------------------------------------------------------------------
# Logika subnet
# ---------------------------------------------------------------------------
def hitung_subnet(ip: str, prefix: int) -> dict:
    """Hitung mask, network, broadcast, range host, dan jumlah host (SPEC.md §4.1)."""
    ip_int = _ip_ke_int(ip)
    prefix = _cek_prefix(prefix)

    # Subnet mask: `prefix` bit 1 di kiri, sisanya 0. Contoh /25 -> 255.255.255.128.
    mask = (0xFFFFFFFF << (32 - prefix)) & 0xFFFFFFFF
    # Wildcard: kebalikan mask (bit host bernilai 1).
    wildcard = ~mask & 0xFFFFFFFF

    # Network address = IP AND subnet mask (bit host dibuat 0).
    network = ip_int & mask
    # Broadcast address = network OR wildcard (bit host dibuat 1).
    broadcast = network | wildcard

    if prefix == 32:
        # Host route: satu alamat saja, tanpa broadcast.
        first_host = last_host = ip_int
        broadcast_str = None
        usable = 1
    elif prefix == 31:
        # RFC 3021 point-to-point: kedua alamat dipakai host, tanpa broadcast.
        first_host, last_host = network, broadcast
        broadcast_str = None
        usable = 2
    else:
        first_host, last_host = network + 1, broadcast - 1
        broadcast_str = _int_ke_ip(broadcast)
        usable = 2 ** (32 - prefix) - 2

    return {
        "mask": _int_ke_ip(mask),
        "network": _int_ke_ip(network),
        "broadcast": broadcast_str,
        "first_host": _int_ke_ip(first_host),
        "last_host": _int_ke_ip(last_host),
        "usable_hosts": usable,
    }


# ---------------------------------------------------------------------------
# API
# ---------------------------------------------------------------------------
def _galat(pesan: str) -> JSONResponse:
    return JSONResponse(status_code=400, content={"detail": pesan})


@app.exception_handler(RequestValidationError)
async def _validasi_gagal(request: Request, exc: RequestValidationError) -> JSONResponse:
    # SPEC.md §5: semua kesalahan input menjadi HTTP 400 dengan field "detail" (bukan 422).
    return _galat("Input tidak valid. Periksa kembali isian Anda.")


@app.get("/", include_in_schema=False)
def halaman_utama() -> FileResponse:
    return FileResponse(INDEX_HTML, media_type="text/html")


@app.get("/api/subnet")
def api_subnet(ip: str | None = None, prefix: str | None = None):
    if ip is None:
        return _galat("Parameter 'ip' wajib diisi.")
    if prefix is None or prefix == "":
        return _galat("Parameter 'prefix' wajib diisi (bilangan bulat 0-32).")
    if not re.fullmatch(r"-?[0-9]+", prefix):
        return _galat("Prefix harus bilangan bulat 0-32.")
    try:
        return hitung_subnet(ip, int(prefix))
    except ValueError as e:
        return _galat(str(e))
