# TempCast Malang — MLOps Project

## Deskripsi

TempCast Malang adalah prototipe akademik untuk memprediksi suhu maksimum harian Kota Malang satu hari ke depan (`t+1`) menggunakan pendekatan supervised time-series regression.

Project ini dikembangkan secara bertahap untuk menerapkan konsep MLOps, mulai dari setup environment, dynamic data ingestion, preprocessing, data versioning menggunakan DVC, experiment tracking menggunakan MLflow, Model Registry, automation pipeline menggunakan GitHub Actions, hingga orkestrasi layanan menggunakan Docker Compose.

## Tujuan Proyek

Project ini dirancang untuk:

- menggunakan data cuaca harian Kota Malang,
- memprediksi suhu maksimum hari berikutnya,
- menggunakan Open-Meteo Historical Weather API sebagai sumber data,
- mengambil data secara dinamis dan berkala,
- melakukan preprocessing data secara konsisten,
- melakukan versioning dataset menggunakan DVC,
- melakukan experiment tracking menggunakan MLflow,
- mengelola model menggunakan MLflow Model Registry,
- mengotomasi pipeline MLOps menggunakan GitHub Actions,
- menjalankan layanan ML menggunakan Docker Compose,
- menjaga reproducibility dan data lineage dalam pipeline MLOps.

## Struktur Direktori

```text
MLOps-TempCast-Malang/
├── .devcontainer/
│   ├── Dockerfile
│   └── devcontainer.json
├── .dvc/
│   ├── .gitignore
│   └── config
├── .github/
│   └── workflows/
│       └── mlops-automation.yaml
├── config/
│   └── config.yaml
├── data/
│   ├── raw/
│   │   ├── .gitignore
│   │   └── weather_2025-03-20_to_2026-09-20_20260927_224435.csv.dvc
│   ├── processed/
│   └── README.md
├── docs/
├── models/
├── notebooks/
├── src/
│   ├── data/
│   │   └── __init__.py
│   ├── __init__.py
│   ├── api.py
│   ├── hello.py
│   ├── ingest_data.py
│   ├── main.py
│   └── preprocess.py
├── tests/
│   └── test_smoke.py
├── .dockerignore
├── .dvcignore
├── .gitignore
├── Dockerfile
├── docker-compose.yaml
├── LICENSE
├── pytest.ini
├── requirements.txt
└── README.md
```

## Environment

Project dikembangkan menggunakan GitHub Codespaces.

Versi Python:

```text
Python 3.11
```

Dependency dapat diinstal menggunakan:

```bash
pip install -r requirements.txt
```

## Data Source

Data cuaca berasal dari Open-Meteo Historical Weather API.

Konfigurasi utama:

```text
Location    : Malang
Latitude    : -7.98
Longitude   : 112.63
Timezone    : Asia/Jakarta
Resolution  : Daily
```

Variabel utama:

```text
time
temperature_2m_max
temperature_2m_min
temperature_2m_mean
precipitation_sum
wind_speed_10m_max
```

---

# LK-04 — Dynamic Data Ingestion dan Preprocessing

Pada LK-04, project mengimplementasikan dynamic data ingestion dan preprocessing untuk menyediakan data cuaca yang akan digunakan pada pipeline machine learning.

## Dynamic Data Ingestion

Script ingestion:

```text
src/ingest_data.py
```

Menjalankan ingestion:

```bash
python src/ingest_data.py
```

Pada implementasi terakhir, ingestion menggunakan window 550 hari.

Contoh dataset:

```text
weather_2025-03-20_to_2026-09-20_20260927_224435.csv
```

Dataset awal memiliki:

```text
550 baris
```

## Data Preprocessing

Script preprocessing:

```text
src/preprocess.py
```

Menjalankan preprocessing:

```bash
python src/preprocess.py
```

Tahapan preprocessing mencakup:

- validasi kolom,
- konversi timestamp,
- konversi tipe data numerik,
- penanganan missing value,
- penghapusan duplikasi berdasarkan waktu,
- pengurutan data,
- feature engineering.

---

# LK-05 — Manajemen Data Versioning Menggunakan DVC

Pada LK-05, Data Version Control (DVC) digunakan untuk melakukan versioning dataset hasil ingestion.

DVC digunakan karena Git tidak dirancang untuk menyimpan dataset besar secara langsung.

Dengan DVC:

- Git menyimpan file metadata `.dvc`,
- dataset dikelola oleh DVC,
- perubahan dataset dapat dilacak,
- versi data dapat dibandingkan,
- eksperimen menjadi lebih reproducible,
- data lineage lebih mudah diaudit.

## Inisialisasi DVC

Versi DVC:

```text
3.67.1
```

Inisialisasi:

```bash
dvc init
```

File yang dihasilkan:

```text
.dvc/.gitignore
.dvc/config
.dvcignore
```

Commit:

```text
e5586f9 chore: initialize DVC for LK5
```

## Tracking Dataset Versi 1

Dataset awal:

```text
data/raw/weather_2025-03-20_to_2026-09-20_20260927_224435.csv
```

Tracking Git dihentikan menggunakan:

```bash
git rm --cached data/raw/weather_2025-03-20_to_2026-09-20_20260927_224435.csv
```

Dataset kemudian dilacak menggunakan:

```bash
dvc add data/raw/weather_2025-03-20_to_2026-09-20_20260927_224435.csv
```

Metadata:

```text
data/raw/weather_2025-03-20_to_2026-09-20_20260927_224435.csv.dvc
```

Dataset Versi 1:

```text
md5: cd8922786d870785c30fa23fe91b4947
size: 19079
rows: 550
```

Commit:

```text
76533cd data: track initial LK5 dataset with DVC
```

## Simulasi Continual Learning

Ingestion dijalankan kembali:

```bash
python src/ingest_data.py
```

Dataset baru:

```text
weather_2025-04-02_to_2026-10-03_20261010_101851.csv
```

Dataset awal dan dataset baru digabungkan.

Duplikasi pada kolom `time` dihapus setelah data diurutkan.

Hasil:

```text
Rows V1: 550
Rows ingestion baru: 550
Rows V2 setelah merge + dedup: 563
Periode V2: 2025-03-20 sampai 2026-10-03
```

Dataset bertambah:

```text
13 observasi baru
```

## Deteksi Perubahan oleh DVC

Perintah:

```bash
dvc status
```

Hasil:

```text
changed outs:
    modified:
        data/raw/weather_2025-03-20_to_2026-09-20_20260927_224435.csv
```

Hal tersebut menunjukkan bahwa isi dataset telah berubah.

## Dataset Versi 2

Metadata diperbarui menggunakan:

```bash
dvc add data/raw/weather_2025-03-20_to_2026-09-20_20260927_224435.csv
```

Metadata Versi 2:

```text
md5: 24049e0aa0e75db53f723b4833037b93
size: 19528
```

Perbandingan:

```text
Versi 1:
md5: cd8922786d870785c30fa23fe91b4947
size: 19079

Versi 2:
md5: 24049e0aa0e75db53f723b4833037b93
size: 19528
```

Commit:

```text
8151a3f data: update LK5 dataset to version 2
```

## Audit Versi

Perbandingan menggunakan:

```bash
dvc diff 76533cd 8151a3f --show-hash
```

Hasil:

```text
Modified:
    cd892278..24049e0a  data/raw/weather_2025-03-20_to_2026-09-20_20260927_224435.csv

files summary: 1 modified
```

Perubahan metadata juga dapat diperiksa menggunakan:

```bash
git diff -- data/raw/weather_2025-03-20_to_2026-09-20_20260927_224435.csv.dvc
```

## Sinkronisasi DVC

Status:

```text
Data and pipelines are up to date.
```

Artinya dataset lokal sesuai dengan metadata DVC aktif.

## Data Lineage

Histori utama:

```text
bc40083 chore: configure DVC remote storage
8151a3f data: update LK5 dataset to version 2
76533cd data: track initial LK5 dataset with DVC
e5586f9 chore: initialize DVC for LK5
```

DVC membantu menjaga:

- reproducibility,
- audit perubahan data,
- data lineage,
- debugging,
- continual learning.

---

# LK-06 — Experiment Tracking Menggunakan MLflow

Pada LK-06, proses training dan evaluasi model dicatat menggunakan MLflow Experiment Tracking.

MLflow digunakan untuk menyimpan informasi setiap eksperimen sehingga hasil beberapa model dapat dibandingkan secara konsisten.

## Eksperimen

Total eksperimen:

```text
4 runs
```

Model terbaik:

```text
Linear Regression
```

Metric model terbaik:

```text
MAE  : 0.8297
RMSE : 1.0349
R2   : 0.4549
```

Model menggunakan:

```text
11 fitur
```

## Experiment Tracking

Setiap run mencatat:

- model,
- parameter eksperimen,
- metric evaluasi,
- artifact model,
- informasi run.

Dengan mekanisme ini, proses pemilihan model dapat ditelusuri melalui MLflow.

## Model Terbaik

Linear Regression dipilih sebagai model terbaik pada LK-06.

Model tersebut kemudian digunakan sebagai dasar untuk proses Model Registry pada LK-07.

---

# LK-07 — Model Registry, Versioning, dan Kesiapan Inferensi

Pada LK-07, model terbaik dari LK-06 dikelola menggunakan MLflow Model Registry untuk mendukung versioning dan kesiapan inference.

## Model Versioning

Registered Model:

```text
TempCast-Malang-Best-Model
```

Versi:

| Version | Model | Feature Count | MAE | RMSE | R2 | Stage |
|---|---|---:|---:|---:|---:|---|
| v1 | Linear Regression | 11 | 0.8297 | 1.0349 | 0.4549 | None |
| v2 | Linear Regression | 12 | 0.8113 | 1.0107 | 0.4801 | Production |

Model v2 menggunakan satu fitur tambahan yaitu:

```text
temperature_2m_max
```

Jumlah fitur berubah dari 11 menjadi 12.

## Active Production Model

Model aktif:

```text
Registered Model : TempCast-Malang-Best-Model
Version          : 2
Stage            : Production
Run              : linear_regression_v2_extra_current_temp
```

Version 2 dipilih karena menghasilkan:

- MAE lebih rendah,
- RMSE lebih rendah,
- R2 lebih tinggi.

## Model Lifecycle

Transisi:

```text
None -> Staging -> Production
```

Alur tersebut mensimulasikan lifecycle model sebelum digunakan untuk inference.

## Data Lineage

Model Production terhubung dengan dataset LK-05:

```text
Dataset         : data/raw/weather_2025-03-20_to_2026-09-20_20260927_224435.csv
Dataset Version : LK05_V2
DVC MD5         : 24049e0aa0e75db53f723b4833037b93
Metadata Model  : models/lk07_production_model.yaml
```

## Inference Verification

Model Production dapat dimuat menggunakan:

```python
mlflow.pyfunc.load_model(
    "models:/TempCast-Malang-Best-Model/Production"
)
```

Hasil pengujian inference:

```text
30.71120928
```

Model Production siap digunakan pada tahapan berikutnya.

---

# LK-08 — Otomasi Pipeline MLOps Menggunakan GitHub Actions

Pada LK-08, pipeline MLOps diotomasi menggunakan GitHub Actions.

Workflow menjalankan proses testing dan pipeline machine learning secara otomatis.

## Branch LK-08

```text
experiment/lk8-automation
```

## Workflow

File workflow:

```text
.github/workflows/mlops-automation.yaml
```

## DVC Remote

DVC remote terhubung dengan DagsHub:

```text
dagshub.com/alyaarhm/MLOps-TempCast-Malang
```

GitHub Actions menggunakan secret:

```text
DAGSHUB_TOKEN
```

untuk mengakses remote secara aman.

## Tahapan Automation

Pipeline menjalankan:

1. Checkout repository.
2. Setup Python environment.
3. Install dependencies.
4. Menjalankan testing.
5. Mengambil dataset menggunakan DVC.
6. Menjalankan training model.
7. Mengevaluasi performa model.
8. Melakukan validasi.
9. Melanjutkan proses model jika pipeline berhasil.

## DVC Pull

Dataset dapat diperoleh menggunakan:

```bash
dvc pull
```

Dengan mekanisme tersebut, workflow dapat mengambil dataset tanpa menyimpan file data besar langsung di Git.

## Hasil Pipeline

Workflow GitHub Actions berhasil menjalankan pipeline secara end-to-end.

Implementasi automation membantu:

- mengurangi proses manual,
- meningkatkan consistency,
- menjaga reproducibility,
- mempermudah eksekusi pipeline.

---

# LK-09 — Orkestrasi Layanan ML Terintegrasi Menggunakan Docker Compose

Pada LK-09, layanan TempCast Malang diorkestrasi menggunakan Docker Compose.

Tujuan utamanya adalah menjalankan:

- inference API,
- MLflow Tracking Server,
- PostgreSQL,

sebagai satu sistem multi-container yang saling terhubung.

## Arsitektur Service

Service utama:

```text
postgres-db
     ↓
mlflow-server
     ↓
api-service
```

### postgres-db

PostgreSQL digunakan sebagai backend metadata MLflow.

### mlflow-server

MLflow Server digunakan sebagai:

- tracking server,
- Model Registry,
- penyedia metadata model.

### api-service

FastAPI digunakan untuk:

- health check,
- membaca informasi model,
- melakukan inference.

## Docker Compose

Konfigurasi orkestrasi disimpan pada:

```text
docker-compose.yaml
```

Seluruh service dapat dijalankan menggunakan satu perintah:

```bash
docker compose up -d --build
```

## Custom Bridge Network

Service menggunakan custom Docker network:

```text
tempcast-network
```

Dengan network ini, container dapat mengakses container lain menggunakan service name.

Contoh:

```text
http://mlflow-server:5000
```

API tidak perlu menggunakan IP address container secara langsung.

## Persistent Volumes

Named volume:

```text
postgres_data
mlflow_artifacts
```

### postgres_data

Digunakan untuk menyimpan data PostgreSQL.

### mlflow_artifacts

Digunakan untuk menyimpan artifact MLflow.

Volume membuat data tetap tersedia meskipun container dihentikan.

## Dependency Antar-Service

`depends_on` digunakan untuk mengatur dependency.

Urutan:

```text
postgres-db
→ mlflow-server
→ api-service
```

Healthcheck digunakan agar service berikutnya tidak dijalankan sebelum dependency siap.

## Menjalankan Sistem

Build dan start seluruh service:

```bash
docker compose up -d --build
```

Periksa status:

```bash
docker compose ps
```

Service utama:

```text
postgres-db
mlflow-server
api-service
```

## Verifikasi Komunikasi Antar-Container

Komunikasi dari API menuju MLflow:

```bash
docker compose exec api-service python -c "import requests; r=requests.get('http://mlflow-server:5000/health'); print('Status:', r.status_code); print('Success:', r.status_code == 200)"
```

Hasil:

```text
Status: 200
Success: True
```

Hasil tersebut membuktikan bahwa `api-service` dapat berkomunikasi dengan `mlflow-server` melalui custom Docker network.

## MLflow Model Registry

Model yang digunakan pada LK-09:

```text
TempCast-Malang-LK09-Model
```

Model Version:

```text
3
```

API mengambil model melalui MLflow Model Registry.

## Endpoint `/health`

Health endpoint:

```text
GET /health
```

Pengujian:

```bash
curl http://localhost:8000/health
```

Endpoint digunakan untuk memastikan API berjalan.

## Endpoint `/model-info`

Informasi model:

```bash
curl http://localhost:8000/model-info
```

Contoh response:

```json
{
  "model_name": "TempCast-Malang-LK09-Model",
  "model_version": "3",
  "loaded_from": "MLflow Model Registry",
  "tracking_uri": "http://mlflow-server:5000"
}
```

Response menunjukkan bahwa API berhasil mengambil model dari MLflow Model Registry.

## Endpoint `/predict`

Inference menggunakan:

```text
POST /predict
```

Contoh request:

```bash
curl -X POST http://localhost:8000/predict \
  -H "Content-Type: application/json" \
  -d '{
    "temperature_2m_min": 22.0,
    "temperature_2m_mean": 26.0,
    "precipitation_sum": 1.0,
    "wind_speed_10m_max": 12.0,
    "temperature_2m_max_lag1": 30.0,
    "temperature_2m_max_lag3": 29.5,
    "temperature_2m_max_lag7": 30.2,
    "temperature_2m_max_roll3_mean": 29.8,
    "temperature_2m_max_roll7_mean": 30.0,
    "month": 11,
    "day_of_year": 322
  }'
```

Model menghasilkan prediksi sekitar:

```text
30.5439
```

Hal tersebut menunjukkan bahwa model berhasil digunakan untuk inference melalui API.

## Inter-Container Communication

Alur inference:

```text
User
  ↓
api-service
  ↓
mlflow-server
  ↓
MLflow Model Registry
  ↓
Model
  ↓
Prediction
```

Tracking URI dari API:

```text
http://mlflow-server:5000
```

Hal tersebut membuktikan bahwa layanan tidak bergantung pada `localhost` antar-container.

## Persistence Test

Container dapat dihentikan menggunakan:

```bash
docker compose down
```

Kemudian dijalankan kembali:

```bash
docker compose up -d
```

Named volume tetap tersedia.

Verifikasi volume:

```bash
docker volume ls
```

Dengan demikian:

- data PostgreSQL tetap tersimpan,
- artifact MLflow tetap tersedia,
- model tetap dapat diakses setelah container dijalankan kembali.

## Docker Compose Status

Status seluruh service:

```bash
docker compose ps
```

Output digunakan untuk memastikan semua service berada dalam kondisi berjalan/healthy.

## Menghentikan Sistem

Untuk menghentikan seluruh container:

```bash
docker compose down
```

Volume tidak dihapus oleh perintah tersebut.

Jika seluruh volume juga ingin dihapus:

```bash
docker compose down -v
```

Perintah `-v` tidak digunakan pada pengujian persistence karena akan menghapus named volume.

## Reproducibility LK-09

Clone repository:

```bash
git clone https://github.com/alyaarhm/MLOps-TempCast-Malang
```

Masuk ke repository:

```bash
cd MLOps-TempCast-Malang
```

Pindah ke branch LK-09:

```bash
git switch experiment/lk9-docker-compose
```

Jalankan seluruh sistem:

```bash
docker compose up -d --build
```

Periksa status:

```bash
docker compose ps
```

API dapat diakses melalui:

```text
http://localhost:8000
```

MLflow Server dapat diakses melalui:

```text
http://localhost:5000
```

## Ringkasan LK-09

Pada LK-09, TempCast Malang berhasil dijalankan sebagai sistem multi-container menggunakan Docker Compose.

Sistem terdiri dari:

- PostgreSQL,
- MLflow Server,
- FastAPI inference service.

Ketiga service berhasil berkomunikasi melalui custom bridge network `tempcast-network`.

Persistent volume `postgres_data` dan `mlflow_artifacts` digunakan untuk menjaga data tetap tersedia setelah container direstart.

Dependency antar-service dikelola menggunakan `depends_on` dan healthcheck.

Model `TempCast-Malang-LK09-Model` berhasil dimuat dari MLflow Model Registry dan digunakan oleh API untuk menghasilkan prediction.

Seluruh sistem dapat direplikasi menggunakan satu perintah:

```bash
docker compose up -d --build
```

---

# License

Project ini menggunakan MIT License.