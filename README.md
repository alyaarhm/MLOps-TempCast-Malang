# TempCast Malang — MLOps Project

## Deskripsi

TempCast Malang adalah prototipe akademik untuk memprediksi suhu maksimum harian Kota Malang satu hari ke depan (`t+1`) menggunakan pendekatan supervised time-series regression.

Pada LK-02, fokus utama adalah membangun fondasi teknis proyek MLOps berupa repository GitHub, GitHub Codespaces, struktur direktori terstandar, dependency management, dan GitHub Flow.

Pada LK-04, proyek dikembangkan lebih lanjut dengan implementasi dynamic data ingestion dan preprocessing untuk mendukung pengambilan serta pengolahan data cuaca secara berkala.

## Tujuan Proyek

Proyek ini dirancang untuk:
- menggunakan data cuaca harian Kota Malang,
- melakukan prediksi suhu maksimum hari berikutnya,
- menggunakan Open-Meteo Historical Weather API sebagai sumber data,
- menyiapkan fondasi pengembangan MLOps yang reproducible,
- mendukung pengambilan data dinamis secara berkala,
- melakukan preprocessing data secara konsisten.

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
├── docs/
├── models/
│   ├── .gitkeep
│   └── README.md
├── notebooks/
│   └── README.md
├── src/
│   ├── data/
│   │   └── __init__.py
│   ├── __init__.py
│   ├── hello.py
│   ├── ingest_data.py
│   ├── main.py
│   └── preprocess.py
├── tests/
│   └── test_smoke.py
├── pytest.ini
├── requirements.txt
├── .gitignore
├── LICENSE
└── README.md