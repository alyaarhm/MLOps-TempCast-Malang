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
```

## GitHub Codespaces

Project dikembangkan menggunakan GitHub Codespaces agar environment pengembangan konsisten dan reproducible.

Environment utama menggunakan Python 3.11.

Untuk menginstal seluruh dependency project:

```bash
pip install -r requirements.txt
```

## Menjalankan Project

Untuk menjalankan konfigurasi utama project:

```bash
python src/main.py
```

Untuk menjalankan initial environment test:

```bash
python src/hello.py
```

Untuk menjalankan automated test:

```bash
pytest
```

## Konfigurasi TempCast Malang

Konfigurasi utama project disimpan pada:

```text
config/config.yaml
```

Konfigurasi tersebut memuat informasi utama seperti:

- nama project,
- jenis task,
- target prediksi,
- lokasi Kota Malang,
- latitude dan longitude,
- timezone,
- sumber data,
- frekuensi pengambilan data,
- kandidat model,
- metrik evaluasi.

## LK-04: Dynamic Data Ingestion dan Preprocessing

Pada LK-04, TempCast Malang mengimplementasikan proses penarikan data cuaca secara dinamis dari Open-Meteo Historical Weather API dan melakukan preprocessing secara otomatis.

### Data Ingestion

Script data ingestion tersedia pada:

```text
src/ingest_data.py
```

Untuk menjalankan ingestion:

```bash
python src/ingest_data.py
```

Proses ingestion melakukan:

- pengambilan data cuaca harian dari Open-Meteo API,
- pengambilan data berdasarkan koordinat Kota Malang,
- penggunaan timezone `Asia/Jakarta`,
- pengambilan data menggunakan window 550 hari,
- validasi HTTP response,
- timeout handling,
- retry ketika request mengalami kegagalan,
- validasi response kosong,
- konversi response JSON menjadi DataFrame,
- penyimpanan raw data dalam format CSV.

Hasil ingestion disimpan pada:

```text
data/raw/
```

Contoh file raw hasil ingestion:

```text
weather_2025-03-20_to_2026-09-20_20260927_224435.csv
```

Pada pengujian terbaru, proses ingestion berhasil mengambil 550 baris data cuaca harian.

### Mekanisme Non-Destructive

Setiap proses ingestion menghasilkan nama file yang mengandung timestamp.

Dengan mekanisme ini, file hasil ingestion sebelumnya tidak tertimpa ketika script dijalankan kembali.

Contoh pola nama file:

```text
weather_<start_date>_to_<end_date>_<timestamp>.csv
```

Mekanisme tersebut digunakan untuk mensimulasikan proses pengambilan data secara periodik.

### Simulasi Pengambilan Data Periodik

Script ingestion dapat dijalankan berulang menggunakan:

```bash
python src/ingest_data.py
```

Untuk melihat hasil ingestion:

```bash
ls -lt data/raw
```

Setiap eksekusi menghasilkan file baru sehingga riwayat data tetap tersedia.

## Data Preprocessing

Script preprocessing tersedia pada:

```text
src/preprocess.py
```

Untuk menjalankan preprocessing:

```bash
python src/preprocess.py
```

Tahapan preprocessing meliputi:

- validasi struktur kolom,
- konversi kolom waktu menjadi tipe datetime,
- konversi nilai cuaca menjadi tipe numerik,
- pemeriksaan dan penanganan missing value,
- penghapusan data duplikat berdasarkan tanggal,
- pengurutan data secara kronologis,
- pembuatan lag feature,
- pembuatan rolling mean feature,
- pembuatan calendar feature,
- pembentukan target suhu maksimum hari berikutnya (`t+1`).

Pada pengujian terbaru diperoleh:

```text
Raw files loaded: 5
Rows before preprocessing: 647
Rows after cleaning: 557
Rows after feature engineering: 549
```

Hasil preprocessing disimpan pada:

```text
data/processed/
```

Contoh file processed:

```text
tempcast_features_20260927_224501.csv
```

## Feature Engineering

Feature yang dihasilkan antara lain:

```text
temperature_2m_max_lag1
temperature_2m_max_lag3
temperature_2m_max_lag7
temperature_2m_max_roll3_mean
temperature_2m_max_roll7_mean
month
day_of_year
temperature_2m_max_t_plus_1
```

Feature tersebut digunakan sebagai dasar untuk tahap pengembangan model machine learning berikutnya.

## Data Pipeline

Alur data TempCast Malang:

```text
Open-Meteo API
        ↓
Data Ingestion
        ↓
data/raw/
        ↓
Data Cleaning
        ↓
Feature Engineering
        ↓
data/processed/
```

Pipeline tersebut memungkinkan data baru diambil secara berkala dan diproses secara konsisten sebelum digunakan pada tahap modeling.

## Pengujian

Pengujian project dilakukan menggunakan `pytest`.

Jalankan:

```bash
pytest
```

Hasil pengujian terbaru:

```text
1 passed
```

Syntax script juga telah diperiksa menggunakan:

```bash
python -m py_compile src/ingest_data.py src/preprocess.py
```

Panjang baris pada kedua script juga telah diperiksa agar tidak melebihi 79 karakter.

## Branching Strategy

Project menggunakan GitHub Flow.

Implementasi LK-04 dikembangkan pada branch:

```text
experiment/lk4-data-ingestion
```

Branch tersebut memuat:

- `src/ingest_data.py`,
- `src/preprocess.py`,
- sampel raw data,
- dokumentasi proses ingestion dan preprocessing.

## Repository

Repository public:

```text
https://github.com/alyaarhm/MLOps-TempCast-Malang
```

Branch LK-04:

```text
experiment/lk4-data-ingestion
```

## Reproducibility

Untuk menjalankan ulang pipeline:

1. Install dependency:

```bash
pip install -r requirements.txt
```

2. Jalankan data ingestion:

```bash
python src/ingest_data.py
```

3. Jalankan preprocessing:

```bash
python src/preprocess.py
```

4. Jalankan pengujian:

```bash
pytest
```

Dengan langkah tersebut, proses ingestion dan preprocessing dapat direproduksi pada GitHub Codespaces.

## License

Project ini menggunakan MIT License.
