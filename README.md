# TempCast Malang — MLOps Project

## Deskripsi

TempCast Malang adalah prototipe akademik untuk memprediksi suhu maksimum harian Kota Malang satu hari ke depan (`t+1`) menggunakan pendekatan supervised time-series regression.

Pada LK-02, fokus utama adalah membangun fondasi teknis proyek MLOps berupa repository GitHub, GitHub Codespaces, struktur direktori terstandar, dependency management, dan GitHub Flow.

## Tujuan Proyek

Proyek ini dirancang untuk:
- menggunakan data cuaca harian Kota Malang,
- melakukan prediksi suhu maksimum hari berikutnya,
- menggunakan Open-Meteo Historical Weather API sebagai sumber data,
- menyiapkan fondasi pengembangan MLOps yang reproducible.

## Struktur Direktori

```text
MLOps-TempCast-Malang/
├── .devcontainer/
│   └── devcontainer.json
├── config/
│   └── config.yaml
├── data/
│   ├── raw/
│   ├── processed/
│   └── README.md
├── models/
│   └── README.md
├── notebooks/
│   └── README.md
├── src/
│   ├── __init__.py
│   ├── hello.py
│   └── main.py
├── tests/
│   └── test_smoke.py
├── pytest.ini
├── requirements.txt
├── .gitignore
├── LICENSE
└── README.md