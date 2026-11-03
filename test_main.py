"""Test Kalkulator Subnet, diturunkan dari SPEC.md §7.1, §7.2, dan §7.4 (A1-A4).

Kasus VLSM (§7.3, A5-A6) belum ditulis di sini; dikerjakan di issue VLSM.
"""

import pytest
from fastapi.testclient import TestClient

from main import app, hitung_subnet

client = TestClient(app)


# ---------------------------------------------------------------------------
# SPEC.md §7.1 — hitung_subnet: kasus valid
# ---------------------------------------------------------------------------
KASUS_VALID = [
    pytest.param(
        "172.16.5.130", 25,
        {
            "mask": "255.255.255.128",
            "network": "172.16.5.128",
            "broadcast": "172.16.5.255",
            "first_host": "172.16.5.129",
            "last_host": "172.16.5.254",
            "usable_hosts": 126,
        },
        id="S1-prefix-25",
    ),
    pytest.param(
        "10.0.0.0", 30,
        {
            "mask": "255.255.255.252",
            "network": "10.0.0.0",
            "broadcast": "10.0.0.3",
            "first_host": "10.0.0.1",
            "last_host": "10.0.0.2",
            "usable_hosts": 2,
        },
        id="S2-prefix-30",
    ),
    pytest.param(
        "192.168.1.0", 31,
        {
            "mask": "255.255.255.254",
            "network": "192.168.1.0",
            "broadcast": None,
            "first_host": "192.168.1.0",
            "last_host": "192.168.1.1",
            "usable_hosts": 2,
        },
        id="S3-prefix-31-point-to-point",
    ),
    pytest.param(
        "192.168.1.5", 32,
        {
            "mask": "255.255.255.255",
            "network": "192.168.1.5",
            "broadcast": None,
            "first_host": "192.168.1.5",
            "last_host": "192.168.1.5",
            "usable_hosts": 1,
        },
        id="S4-prefix-32-host-tunggal",
    ),
    pytest.param(
        "192.168.1.10", 24,
        {
            "mask": "255.255.255.0",
            "network": "192.168.1.0",
            "broadcast": "192.168.1.255",
            "first_host": "192.168.1.1",
            "last_host": "192.168.1.254",
            "usable_hosts": 254,
        },
        id="S5-prefix-24",
    ),
    pytest.param(
        "10.10.10.10", 20,
        {
            "mask": "255.255.240.0",
            "network": "10.10.0.0",
            "broadcast": "10.10.15.255",
            "first_host": "10.10.0.1",
            "last_host": "10.10.15.254",
            "usable_hosts": 4094,
        },
        id="S6-prefix-20-lintas-oktet",
    ),
    pytest.param(
        "10.1.2.3", 8,
        {
            "mask": "255.0.0.0",
            "network": "10.0.0.0",
            "broadcast": "10.255.255.255",
            "first_host": "10.0.0.1",
            "last_host": "10.255.255.254",
            "usable_hosts": 16777214,
        },
        id="S7-prefix-8",
    ),
    pytest.param(
        "0.0.0.0", 0,
        {
            "mask": "0.0.0.0",
            "network": "0.0.0.0",
            "broadcast": "255.255.255.255",
            "first_host": "0.0.0.1",
            "last_host": "255.255.255.254",
            "usable_hosts": 4294967294,
        },
        id="S8-prefix-0",
    ),
    pytest.param(
        "192.168.1.255", 24,
        {
            "mask": "255.255.255.0",
            "network": "192.168.1.0",
            "broadcast": "192.168.1.255",
            "first_host": "192.168.1.1",
            "last_host": "192.168.1.254",
            "usable_hosts": 254,
        },
        id="S9-ip-sama-dengan-broadcast",
    ),
]


@pytest.mark.parametrize("ip, prefix, harapan", KASUS_VALID)
def test_hitung_subnet_valid(ip, prefix, harapan):
    assert hitung_subnet(ip, prefix) == harapan


# ---------------------------------------------------------------------------
# SPEC.md §7.2 — hitung_subnet: kasus ditolak (ValueError)
# ---------------------------------------------------------------------------
KASUS_DITOLAK = [
    pytest.param("256.1.1.1", 24, id="E1-oktet-lebih-dari-255"),
    pytest.param("192.168.01.1", 24, id="E2-nol-di-depan"),
    pytest.param("192.168.1", 24, id="E3-hanya-3-oktet"),
    pytest.param("abc", 24, id="E4-bukan-angka"),
    pytest.param("", 24, id="E5-kosong"),
    pytest.param("192.168.1.1", 33, id="E6-prefix-33"),
    pytest.param("192.168.1.1", -1, id="E7-prefix-negatif"),
    pytest.param("1.2.3.4.5", 24, id="E8-lima-oktet"),
    pytest.param(" 192.168.1.1", 24, id="E9-ada-spasi"),
    pytest.param("192.168.-1.1", 24, id="E10-oktet-negatif"),
]


@pytest.mark.parametrize("ip, prefix", KASUS_DITOLAK)
def test_hitung_subnet_ditolak(ip, prefix):
    with pytest.raises(ValueError):
        hitung_subnet(ip, prefix)


# ---------------------------------------------------------------------------
# SPEC.md §7.4 — API (A1-A4)
# ---------------------------------------------------------------------------
def test_a1_halaman_utama():
    r = client.get("/")
    assert r.status_code == 200
    assert "<html" in r.text.lower()


@pytest.mark.parametrize(
    "ip, prefix, harapan",
    [p for p in KASUS_VALID if p.id.startswith(("S1-", "S3-", "S4-"))],
)
def test_a2_api_subnet_sukses(ip, prefix, harapan):
    r = client.get("/api/subnet", params={"ip": ip, "prefix": prefix})
    assert r.status_code == 200
    assert r.json() == harapan


@pytest.mark.parametrize("ip, prefix", KASUS_DITOLAK)
def test_a3_api_subnet_input_tidak_valid(ip, prefix):
    r = client.get("/api/subnet", params={"ip": ip, "prefix": prefix})
    assert r.status_code == 400
    assert r.json()["detail"]


@pytest.mark.parametrize(
    "params",
    [
        pytest.param({"ip": "192.168.1.1"}, id="A4-prefix-hilang"),
        pytest.param({"prefix": "24"}, id="A4-ip-hilang"),
        pytest.param({"ip": "192.168.1.1", "prefix": "abc"}, id="A4-prefix-bukan-angka"),
        pytest.param({"ip": "192.168.1.1", "prefix": "24.5"}, id="A4-prefix-pecahan"),
    ],
)
def test_a4_api_subnet_parameter_salah(params):
    r = client.get("/api/subnet", params=params)
    assert r.status_code == 400
    assert r.json()["detail"]
