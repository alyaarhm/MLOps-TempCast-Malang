# TempCast Malang — MLOps Project

## Deskripsi

TempCast Malang adalah prototipe akademik untuk memprediksi suhu maksimum harian Kota Malang satu hari ke depan (`t+1`) menggunakan pendekatan supervised time-series regression.

Project ini dikembangkan secara bertahap untuk menerapkan konsep MLOps, mulai dari setup environment, dynamic data ingestion, preprocessing, data versioning, experiment tracking, model registry, automation pipeline, orkestrasi layanan, hingga model serving dan scaling.

## Tujuan Proyek

Project ini dirancang untuk:

- menggunakan data cuaca harian Kota Malang,
- memprediksi suhu maksimum hari berikutnya,
- menggunakan Open-Meteo Historical Weather API sebagai sumber data,
- mengambil data secara dinamis dan berkala,
- melakukan preprocessing data secara konsisten,
- melakukan versioning dataset menggunakan DVC,
- melakukan experiment tracking menggunakan MLflow,
- mengelola model melalui MLflow Model Registry,
- mengotomasi pipeline MLOps,
- menjalankan layanan menggunakan Docker Compose,
- melakukan model serving dan horizontal scaling,
- menjaga reproducibility dan data lineage.

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
│   ├── processed/
│   └── README.md
├── models/
├── notebooks/
├── src/
│   ├── __init__.py
│   ├── api.py
│   ├── evaluate_and_register.py
│   ├── ingest_data.py
│   ├── main.py
│   ├── preprocess.py
│   ├── train.py
│   └── train_lk7_v2.py
├── tests/
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

Variabel yang digunakan antara lain:

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

Pada LK-04, project mulai menggunakan dynamic data ingestion untuk mengambil data cuaca secara otomatis dan melakukan preprocessing sebelum data digunakan pada tahap berikutnya.

## Dynamic Data Ingestion

Script ingestion:

```text
src/ingest_data.py
```

Untuk menjalankan ingestion:

```bash
python src/ingest_data.py
```

Pada implementasi terakhir, ingestion menggunakan window 550 hari.

Contoh hasil ingestion:

```text
weather_2025-03-20_to_2026-09-20_20260927_224435.csv
```

Dataset awal yang digunakan memiliki:

```text
550 baris
```

## Data Preprocessing

Script preprocessing:

```text
src/preprocess.py
```

Jalankan:

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

DVC digunakan karena Git tidak dirancang untuk menyimpan file dataset besar secara langsung.

Dengan DVC:

- Git menyimpan file metadata `.dvc`,
- file dataset dikelola oleh DVC,
- perubahan dataset dapat dilacak,
- versi data dapat dibandingkan,
- proses eksperimen menjadi lebih reproducible,
- data lineage lebih mudah diaudit.

## Inisialisasi DVC

Versi DVC yang digunakan:

```text
3.67.1
```

DVC diinisialisasi menggunakan:

```bash
dvc init
```

Setelah proses inisialisasi, file berikut ditambahkan:

```text
.dvc/.gitignore
.dvc/config
.dvcignore
```

Commit inisialisasi:

```text
e5586f9 chore: initialize DVC for LK5
```

## Tracking Dataset Versi 1

Dataset awal:

```text
data/raw/weather_2025-03-20_to_2026-09-20_20260927_224435.csv
```

Karena file tersebut sebelumnya sudah dilacak oleh Git, tracking Git dihentikan menggunakan:

```bash
git rm --cached data/raw/weather_2025-03-20_to_2026-09-20_20260927_224435.csv
```

Selanjutnya dataset dilacak menggunakan DVC:

```bash
dvc add data/raw/weather_2025-03-20_to_2026-09-20_20260927_224435.csv
```

File metadata yang dihasilkan:

```text
data/raw/weather_2025-03-20_to_2026-09-20_20260927_224435.csv.dvc
```

Metadata Dataset Versi 1:

```text
md5: cd8922786d870785c30fa23fe91b4947
size: 19079
```

Jumlah data:

```text
550 baris
```

Commit Dataset Versi 1:

```text
76533cd data: track initial LK5 dataset with DVC
```

## Simulasi Continual Learning

Untuk mensimulasikan adanya data baru, ingestion dijalankan kembali:

```bash
python src/ingest_data.py
```

Hasil ingestion baru:

```text
weather_2025-04-02_to_2026-10-03_20261010_101851.csv
```

Dataset awal dan dataset baru kemudian digabungkan.

Untuk menghindari duplikasi, data diurutkan berdasarkan waktu dan duplikasi pada kolom `time` dihapus.

Hasil simulasi:

```text
Rows V1: 550
Rows ingestion baru: 550
Rows V2 setelah merge + dedup: 563
Periode V2: 2025-03-20 sampai 2026-10-03
```

Dataset bertambah sebanyak:

```text
13 observasi baru
```

## Deteksi Perubahan oleh DVC

Setelah dataset diperbarui, perintah:

```bash
dvc status
```

mendeteksi perubahan:

```text
changed outs:
    modified:
        data/raw/weather_2025-03-20_to_2026-09-20_20260927_224435.csv
```

Hal ini menunjukkan bahwa isi dataset sudah berbeda dengan metadata Versi 1.

## Dataset Versi 2

Metadata DVC diperbarui kembali menggunakan:

```bash
dvc add data/raw/weather_2025-03-20_to_2026-09-20_20260927_224435.csv
```

Metadata Dataset Versi 2:

```text
md5: 24049e0aa0e75db53f723b4833037b93
size: 19528
```

Perubahan metadata:

```text
Versi 1:
md5: cd8922786d870785c30fa23fe91b4947
size: 19079

Versi 2:
md5: 24049e0aa0e75db53f723b4833037b93
size: 19528
```

Commit Dataset Versi 2:

```text
8151a3f data: update LK5 dataset to version 2
```

## Audit dan Perbandingan Versi

Perbandingan antarversi dilakukan menggunakan:

```bash
dvc diff 76533cd 8151a3f --show-hash
```

Hasil:

```text
Modified:
    cd892278..24049e0a  data/raw/weather_2025-03-20_to_2026-09-20_20260927_224435.csv

files summary: 1 modified
```

Hasil tersebut menunjukkan bahwa Dataset Versi 1 dan Dataset Versi 2 memiliki hash yang berbeda.

Perbandingan file metadata `.dvc`:

```bash
git diff -- data/raw/weather_2025-03-20_to_2026-09-20_20260927_224435.csv.dvc
```

Perubahan yang tercatat:

```text
- md5: cd8922786d870785c30fa23fe91b4947
- size: 19079

+ md5: 24049e0aa0e75db53f723b4833037b93
+ size: 19528
```

## Sinkronisasi DVC

Setelah metadata DVC diperbarui, status menunjukkan:

```text
Data and pipelines are up to date.
```

Artinya dataset lokal sudah sesuai dengan metadata DVC yang aktif.

## DVC Remote Storage

Data DVC dikirim ke remote menggunakan:

```bash
dvc push
```

DVC remote kemudian digunakan pada tahapan berikutnya agar dataset dapat diambil kembali secara reproducible.

## Data Lineage

Histori perubahan dataset dapat ditelusuri melalui kombinasi Git dan DVC.

Histori utama LK-05:

```text
bc40083 chore: configure DVC remote storage
8151a3f data: update LK5 dataset to version 2
76533cd data: track initial LK5 dataset with DVC
e5586f9 chore: initialize DVC for LK5
```

Dengan mekanisme ini dapat diketahui:

- versi dataset,
- perubahan hash,
- perubahan ukuran data,
- waktu perubahan,
- konfigurasi remote.

## Reproducibility

Untuk mendapatkan project:

```bash
git clone https://github.com/alyaarhm/MLOps-TempCast-Malang
```

Pindah ke branch LK-05:

```bash
git switch experiment/lk5-dvc-versioning
```

Install dependency:

```bash
pip install -r requirements.txt
pip install dvc
```

Ambil dataset dari DVC remote:

```bash
dvc pull
```

Cek status:

```bash
dvc status
```

---

# LK-06 — Experiment Tracking Menggunakan MLflow

Pada LK-06, proses training model mulai dicatat menggunakan MLflow Experiment Tracking.

Tujuannya adalah agar setiap eksperimen dapat dibandingkan berdasarkan parameter, metric, dan model yang dihasilkan.

## Experiment Tracking

Beberapa eksperimen model dijalankan dan dicatat menggunakan MLflow.

Total run yang dibandingkan:

```text
4 runs
```

Model terbaik pada LK-06 adalah:

```text
Linear Regression
```

Metric model terbaik:

```text
MAE  : 0.8297
RMSE : 1.0349
R2   : 0.4549
```

Jumlah fitur yang digunakan:

```text
11 fitur
```

## Hasil Eksperimen

Hasil eksperimen juga disimpan pada:

```text
lk06_experiment_results.csv
```

Dengan MLflow, metric tiap eksperimen dapat dibandingkan sehingga pemilihan model tidak hanya dilakukan secara manual.

## Model Terbaik

Linear Regression dipilih sebagai model terbaik LK-06 karena memberikan performa terbaik dari beberapa eksperimen yang dilakukan.

Model ini kemudian digunakan sebagai dasar pada LK-07 untuk proses model versioning dan Model Registry.

---

# LK-07 — Model Registry, Versioning, dan Kesiapan Inferensi

Pada LK-07, model terbaik dari LK-06 dikelola menggunakan MLflow Model Registry untuk mendukung versioning dan kesiapan inference.

## Model Versioning

Model terdaftar menggunakan nama:

```text
TempCast-Malang-Best-Model
```

Versi yang tersedia:

| Version | Model | Feature Count | MAE | RMSE | R2 | Stage |
|---|---|---:|---:|---:|---:|---|
| v1 | Linear Regression | 11 | 0.8297 | 1.0349 | 0.4549 | None |
| v2 | Linear Regression | 12 | 0.8113 | 1.0107 | 0.4801 | Production |

Model v2 menggunakan satu fitur tambahan, yaitu `temperature_2m_max`, sehingga jumlah fitur berubah dari 11 menjadi 12.

## Active Production Model

Model yang aktif untuk inference:

- Registered Model: `TempCast-Malang-Best-Model`
- Version: `2`
- Stage: `Production`
- Run: `linear_regression_v2_extra_current_temp`

Version 2 dipilih sebagai Production karena menghasilkan MAE dan RMSE yang lebih rendah serta R2 yang lebih tinggi dibandingkan version 1.

## Model Lifecycle

Transisi stage:

```text
None -> Staging -> Production
```

Transisi tersebut digunakan untuk mensimulasikan alur model dari hasil eksperimen sampai siap digunakan.

## Data Lineage

Model Production tetap terhubung dengan dataset dari LK-05.

```text
Dataset         : data/raw/weather_2025-03-20_to_2026-09-20_20260927_224435.csv
Dataset Version : LK05_V2
DVC MD5         : 24049e0aa0e75db53f723b4833037b93
Metadata Model  : models/lk07_production_model.yaml
```

## Inference Verification

Model Production berhasil dimuat secara programatik menggunakan:

```python
mlflow.pyfunc.load_model("models:/TempCast-Malang-Best-Model/Production")
```

Pengujian menggunakan satu input baru menghasilkan prediksi:

```text
30.71120928
```

Hal ini menunjukkan bahwa model Production telah siap digunakan pada layanan inference.

---

# LK-08 — Otomasi Pipeline MLOps Menggunakan GitHub Actions

Pada LK-08, proses MLOps mulai diotomasi menggunakan GitHub Actions.

Workflow digunakan untuk menjalankan testing, mengambil dataset dari DVC remote, menjalankan training, melakukan validasi performa model, dan mendaftarkan model ke MLflow Model Registry secara otomatis.

## Branch LK-08

Implementasi LK-08 dikembangkan pada:

```text
experiment/lk8-automation
```

## GitHub Actions Workflow

Workflow disimpan pada:

```text
.github/workflows/mlops-automation.yaml
```

Workflow terdiri dari proses testing dan machine learning pipeline.

## DVC Remote

DVC remote pada implementasi LK-08 menggunakan DagsHub.

Repository:

```text
dagshub.com/alyaarhm/MLOps-TempCast-Malang
```

Akses dari GitHub Actions menggunakan secret:

```text
DAGSHUB_TOKEN
```

## Tahapan Pipeline

Pipeline otomatis menjalankan:

1. Checkout repository.
2. Setup Python.
3. Install dependency.
4. Menjalankan testing.
5. Mengambil dataset menggunakan DVC.
6. Menjalankan training.
7. Mengevaluasi performa model.
8. Melakukan validasi threshold.
9. Mendaftarkan model yang lolos ke MLflow Model Registry.

## Testing

Testing dijalankan sebelum proses training.

Tujuannya untuk memastikan kode utama dapat berjalan sebelum pipeline machine learning dilanjutkan.

## Mengambil Dataset

Dataset diambil menggunakan:

```bash
dvc pull
```

Dataset berasal dari DVC remote sehingga file dataset tidak perlu disimpan langsung pada repository Git.

## Training dan Validation

Model dilatih secara otomatis melalui workflow.

Metric hasil training kemudian diperiksa terhadap threshold yang telah ditentukan.

Jika model memenuhi kriteria, pipeline akan melanjutkan ke proses registry.

## Automatic Model Registry

Model yang lolos validasi didaftarkan otomatis ke MLflow Model Registry.

Model hasil automation diarahkan ke:

```text
Staging
```

Dengan demikian, proses dari data sampai model registry dapat dilakukan dalam satu workflow otomatis.

## Menjalankan Workflow

Workflow dapat dijalankan melalui:

```text
GitHub Repository
→ Actions
→ MLOps Automation
```

Workflow LK-08 berhasil berjalan secara end-to-end.

---

# LK-09 — Orkestrasi Layanan ML Menggunakan Docker Compose

Pada LK-09, layanan TempCast Malang diorkestrasi menggunakan Docker Compose agar API inference, MLflow Server, dan database dapat berjalan sebagai satu sistem.

## Service yang Digunakan

Tiga service utama:

- `api-service`: FastAPI untuk layanan inference.
- `mlflow-server`: MLflow Tracking Server dan Model Registry.
- `postgres-db`: PostgreSQL sebagai backend metadata MLflow.

## Docker Image

Project menggunakan:

```text
Dockerfile
```

Dependency container diambil dari:

```text
requirements.txt
```

## Custom Network

Seluruh service menggunakan custom bridge network:

```text
tempcast-network
```

Network ini memungkinkan antar-container berkomunikasi melalui service name.

Contoh:

```text
http://mlflow-server:5000
```

## Persistent Volume

Named volume yang digunakan:

```text
postgres_data
mlflow_artifacts
```

Fungsi:

- `postgres_data` menyimpan database PostgreSQL.
- `mlflow_artifacts` menyimpan artifact MLflow.

Named volume tetap tersedia meskipun container dihentikan.

## Dependency Antar-Service

Startup order diatur menggunakan `depends_on`.

Urutan utama:

```text
postgres-db
→ mlflow-server
→ api-service
```

Healthcheck digunakan agar service berikutnya dijalankan setelah dependency siap digunakan.

## Menjalankan Sistem

Seluruh sistem dapat dibangun dan dijalankan menggunakan satu perintah:

```bash
docker compose up -d --build
```

Cek status:

```bash
docker compose ps
```

Service yang aktif:

```text
tempcast-api
tempcast-mlflow
tempcast-postgres
```

## Verifikasi Komunikasi API ke MLflow

Pengujian:

```bash
docker compose exec api-service python -c "import requests; r=requests.get('http://mlflow-server:5000/health'); print('Status:', r.status_code); print('Success:', r.status_code == 200)"
```

Hasil:

```text
Status: 200
Success: True
```

Hal ini menunjukkan bahwa `api-service` dapat mengakses MLflow melalui service name pada Docker network.

## Model Registry

Model yang digunakan API:

```text
TempCast-Malang-LK09-Model
```

Model dapat diperiksa melalui endpoint:

```bash
curl http://localhost:8000/model-info
```

Contoh hasil:

```json
{
  "model_name": "TempCast-Malang-LK09-Model",
  "model_version": "3",
  "loaded_from": "MLflow Model Registry",
  "tracking_uri": "http://mlflow-server:5000"
}
```

## Endpoint Health

```bash
curl http://localhost:8000/health
```

Contoh hasil:

```json
{
  "status": "healthy",
  "model_loaded": true
}
```

## Endpoint Prediction

Endpoint:

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

Contoh hasil:

```json
{
  "predicted_temperature_max": 30.5439,
  "model_name": "TempCast-Malang-LK09-Model",
  "model_version": "3"
}
```

## Persistence Test

Named volume:

```bash
docker volume ls
```

Container dapat dihentikan menggunakan:

```bash
docker compose down
```

Kemudian dijalankan kembali:

```bash
docker compose up -d
```

Model Registry tetap dapat diakses setelah restart sehingga persistence berjalan sesuai kebutuhan.

## Menghentikan Sistem

```bash
docker compose down
```

---

# LK-10 — Model Serving dan Simulasi Scaling Menggunakan MLflow Models & Docker

Pada LK-10, model yang telah terdaftar di MLflow Model Registry dioperasionalkan menjadi REST API menggunakan MLflow Models.

Model kemudian dibungkus menjadi Docker image dan dijalankan dalam beberapa replika untuk mensimulasikan horizontal scaling.

## Model Production

Model yang digunakan:

```text
Registered Model : TempCast-Malang-LK09-Model
Version          : 3
Stage            : Production
```

Verifikasi model dilakukan menggunakan MLflow Client.

## Menjalankan Model Serving

Model Production dijalankan menggunakan:

```bash
mlflow models serve \
  -m "models:/TempCast-Malang-LK09-Model/Production" \
  -h 0.0.0.0 \
  -p 8080 \
  --no-conda
```

Server MLflow berjalan pada:

```text
http://0.0.0.0:8080
```

## Health Check

Pengujian health endpoint:

```bash
docker compose exec api-service python -c "import requests; r=requests.get('http://localhost:8080/health'); print(r.status_code); print(r.text)"
```

Hasil:

```text
200
```

## Endpoint Inference

Endpoint MLflow Models:

```text
POST /invocations
```

Contoh pengujian:

```bash
docker compose exec -T api-service python - <<'PY'
import requests

payload = {
    "dataframe_records": [{
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
    }]
}

r = requests.post(
    "http://localhost:8080/invocations",
    json=payload
)

print("Status:", r.status_code)
print("Response:", r.text)
PY
```

Hasil:

```text
Status: 200
Response: {"predictions": [30.543929633198587]}
```

Hal ini menunjukkan bahwa model berhasil disajikan sebagai REST API dan memberikan hasil prediction.

## Membuat Docker Image Model

Model Production dibungkus menjadi Docker image menggunakan:

```bash
mlflow models build-docker \
  -m "models:/TempCast-Malang-LK09-Model/Production" \
  -n tempcast-lk10-model
```

Image yang dihasilkan:

```text
tempcast-lk10-model:latest
```

Verifikasi image:

```bash
docker images | grep tempcast-lk10-model
```

## Konfigurasi Model Serving pada Docker Compose

Service `model-serving` ditambahkan pada `docker-compose.yaml`:

```yaml
model-serving:
  image: tempcast-lk10-model:latest
  networks:
    - tempcast-network
  deploy:
    replicas: 3
  restart: unless-stopped
```

Konfigurasi:

```yaml
deploy:
  replicas: 3
```

digunakan untuk mensimulasikan tiga instance model yang berjalan bersamaan.

## Menjalankan Tiga Replika

Jalankan:

```bash
docker compose up -d model-serving
```

Verifikasi:

```bash
docker compose ps
```

Tiga replika yang berjalan:

```text
mlops-tempcast-malang-model-serving-1
mlops-tempcast-malang-model-serving-2
mlops-tempcast-malang-model-serving-3
```

Hal ini menunjukkan bahwa horizontal scaling dengan tiga replika berhasil dilakukan.

## Inference Melalui Service Hasil Scaling

Pengujian dilakukan melalui service name:

```text
http://model-serving:8080/invocations
```

Contoh:

```bash
docker compose exec -T api-service python - <<'PY'
import requests

payload = {
    "dataframe_records": [{
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
    }]
}

r = requests.post(
    "http://model-serving:8080/invocations",
    json=payload
)

print("Status:", r.status_code)
print("Response:", r.text)
PY
```

Hasil:

```text
Status: 200
Response: {"predictions": [30.543929633198587]}
```

Artinya service tetap dapat menerima request inference setelah dijalankan dalam beberapa replika.

## Dynamic Scaling

Jumlah replika dapat ditambah secara dinamis tanpa membangun ulang Docker image.

Menambah dari tiga menjadi empat:

```bash
docker compose up -d --scale model-serving=4 model-serving
```

Verifikasi:

```bash
docker compose ps
```

Instance yang berjalan:

```text
mlops-tempcast-malang-model-serving-1
mlops-tempcast-malang-model-serving-2
mlops-tempcast-malang-model-serving-3
mlops-tempcast-malang-model-serving-4
```

Untuk mengembalikan jumlah replika menjadi tiga:

```bash
docker compose up -d --scale model-serving=3 model-serving
```

## Ringkasan LK-10

Pada LK-10, model Production berhasil dijalankan sebagai REST API menggunakan `mlflow models serve`.

Endpoint `/invocations` dapat menerima data input dan menghasilkan prediksi dengan status HTTP 200.

Model juga berhasil dibungkus menjadi Docker image menggunakan `mlflow models build-docker`.

Docker Compose berhasil menjalankan tiga replika `model-serving`, dan jumlah replika dapat ditingkatkan secara dinamis dari tiga menjadi empat menggunakan opsi `--scale`.

Dengan implementasi tersebut, proses model serving, containerization, dan horizontal scaling dapat dilakukan dalam satu alur yang dapat dijalankan kembali.

---

# License
---

# LK-11 — Implementasi Observability dan Dashboard

Pada LK-11, proyek TempCast Malang dikembangkan dengan menambahkan sistem observability menggunakan Prometheus dan Grafana untuk memantau model machine learning yang telah di-deploy pada LK-10.

Implementasi monitoring mencakup metrik operasional, penggunaan sumber daya, distribusi hasil prediksi, distribusi trafik antar-replika, serta deteksi data drift.

## Branch LK-11

```text
experiment/lk11-observability
```

## Tujuan Implementasi

- Mengintegrasikan Prometheus dan Grafana ke dalam Docker Compose.
- Menyediakan endpoint `/metrics` pada layanan inference.
- Memantau latensi, throughput, error rate, CPU, dan RAM.
- Memvisualisasikan distribusi hasil prediksi model.
- Memantau tiga replika model serving.
- Mengimplementasikan deteksi data drift berdasarkan pergeseran mean fitur input.
- Memberikan peringatan awal terhadap potensi model decay.

## Struktur File LK-11

```text
MLOps-TempCast-Malang/
├── grafana/
│   ├── dashboards/
│   │   └── tempcast-monitoring.json
│   └── provisioning/
│       ├── dashboards/
│       │   └── dashboard.yml
│       └── datasources/
│           └── prometheus.yml
├── src/
│   ├── api.py
│   ├── monitored_model.py
│   ├── load_test.py
│   └── drift_test.py
├── Dockerfile
├── Dockerfile.monitoring
├── docker-compose.yaml
├── prometheus.yml
├── requirements.txt
└── README.md
```

## Arsitektur Monitoring

Docker Compose terdiri dari tujuh service:

| Service | Fungsi | Port |
|---|---|---|
| postgres-db | Backend database MLflow | 5432 internal |
| mlflow-server | Experiment Tracking dan Model Registry | 5000 |
| api-service | FastAPI inference dan monitoring data drift | 8000 |
| model-serving | Model MLflow dengan tiga replika | 8080 internal |
| prometheus | Pengumpulan metrik | 9090 |
| grafana | Visualisasi dashboard | 3000 |
| cadvisor | Monitoring resource container | 8081 |

Seluruh service menggunakan custom bridge network `tempcast-network`.

Alur monitoring:

```text
FastAPI /metrics ───────────────┐
                               │
Model Serving Replica 1 ────────┤
Model Serving Replica 2 ────────┼──> Prometheus ──> Grafana
Model Serving Replica 3 ────────┤
                               │
cAdvisor ──────────────────────┘
```

## Instrumentasi API

Instrumentasi dilakukan menggunakan library `prometheus_client`.

Dependency ditambahkan pada `requirements.txt`:

```text
prometheus-client>=0.21,<1
```

Endpoint FastAPI:

| Endpoint | Method | Fungsi |
|---|---|---|
| /health | GET | Memeriksa kondisi API |
| /model-info | GET | Informasi model |
| /predict | POST | Melakukan inference |
| /metrics | GET | Mengekspos metrik Prometheus |
| /mlflow-check | GET | Memeriksa koneksi ke MLflow |

Endpoint pada kontainer model:

| Endpoint | Method | Fungsi |
|---|---|---|
| /health | GET | Memeriksa kesiapan model |
| /ping | GET | Memeriksa kondisi layanan |
| /invocations | POST | Melakukan inference model |
| /metrics | GET | Mengekspos metrik setiap replika |

## Model Serving dengan Monitoring

Model yang digunakan merupakan model dari LK-10:

```text
Registered Model : TempCast-Malang-LK09-Model
Version          : 3
Stage            : Production pada pengujian LK-10
Base Image       : tempcast-lk10-model:latest
Monitoring Image : tempcast-lk11-model:latest
```

Model digunakan kembali tanpa training ulang.

Docker image monitoring dibangun menggunakan `Dockerfile.monitoring` dengan image LK-10 sebagai base image.

Dependency model disesuaikan dengan file requirements yang tersimpan pada artifact MLflow di `/opt/ml/model/requirements.txt` agar versi library sesuai dengan environment training.

Setiap replika model memiliki identitas tersendiri sehingga Prometheus dapat mengumpulkan metrik secara individual.

## Konfigurasi Prometheus

Konfigurasi scraping disimpan pada file `prometheus.yml` di root project.

```yaml
global:
  scrape_interval: 5s
  evaluation_interval: 5s

scrape_configs:
  - job_name: "tempcast-api"
    metrics_path: /metrics
    static_configs:
      - targets:
          - "api-service:8000"

  - job_name: "tempcast-model"
    metrics_path: /metrics
    dns_sd_configs:
      - names:
          - "model-serving"
        type: A
        port: 8080
        refresh_interval: 5s

  - job_name: "cadvisor"
    static_configs:
      - targets:
          - "cadvisor:8080"

  - job_name: "prometheus"
    static_configs:
      - targets:
          - "prometheus:9090"
```

Prometheus menggunakan DNS service discovery untuk menemukan setiap replika model secara otomatis.

Interval scraping sebesar 5 detik digunakan agar perubahan metrik selama simulasi beban kerja dapat diamati dengan cukup cepat.

## Konfigurasi Grafana

Grafana menggunakan Prometheus sebagai data source.

Data source dikonfigurasi secara otomatis melalui:

```text
grafana/provisioning/datasources/prometheus.yml
```

Dashboard provisioning disimpan pada:

```text
grafana/provisioning/dashboards/dashboard.yml
```

Konfigurasi dashboard disimpan pada:

```text
grafana/dashboards/tempcast-monitoring.json
```

Nama dashboard:

```text
TempCast Malang - ML Observability Dashboard
```

Dengan provisioning, data source dan dashboard dapat dimuat kembali secara otomatis ketika Grafana dijalankan.

## Menjalankan Sistem Monitoring

Clone repository:

```bash
git clone https://github.com/alyaarhm/MLOps-TempCast-Malang
cd MLOps-TempCast-Malang
git switch experiment/lk11-observability
```

Pastikan Docker dan Docker Compose tersedia.

Validasi konfigurasi:

```bash
docker compose config --quiet
```

### Persiapan Base Image LK-10

Image `tempcast-lk10-model:latest` merupakan prasyarat untuk membangun image monitoring LK-11.

Periksa ketersediaan image:

```bash
docker image inspect tempcast-lk10-model:latest
```

Jika image belum tersedia, jalankan layanan registry dan API terlebih dahulu:

```bash
docker compose up -d --build postgres-db mlflow-server api-service
```

Pastikan model yang sesuai telah tersedia di MLflow Model Registry. Untuk mereproduksi pengujian yang sama, gunakan artifact model version 3 dari LK-10.

Setelah MLflow CLI tersedia pada host dan model tersebut dapat diakses dari registry, jalankan:

```bash
export MLFLOW_TRACKING_URI=http://localhost:5000

mlflow models build-docker \
  -m "models:/TempCast-Malang-LK09-Model/3" \
  -n tempcast-lk10-model
```

Apabila menggunakan registry baru, model version 3 asli tidak otomatis tersedia. Artifact model LK-10 perlu dipulihkan atau model dibuat kembali melalui pipeline sebelumnya. Model yang dibuat kembali tidak dijamin identik dengan artifact pengujian asli.

### Build Image LK-11

```bash
docker compose build model-serving api-service
```

Jalankan seluruh layanan apabila kapasitas RAM mencukupi:

```bash
docker compose up -d
```

Periksa status container:

```bash
docker compose ps
```

## Akses Layanan

| Layanan | URL |
|---|---|
| MLflow | http://localhost:5000 |
| FastAPI | http://localhost:8000 |
| API Documentation | http://localhost:8000/docs |
| API Metrics | http://localhost:8000/metrics |
| Prometheus | http://localhost:9090 |
| Prometheus Targets | http://localhost:9090/targets |
| Grafana | http://localhost:3000 |
| cAdvisor | http://localhost:8081 |

Jika menggunakan GitHub Codespaces, akses layanan melalui menu Ports dan Open in Browser.

Grafana menggunakan konfigurasi login awal:

```text
Username: admin
Password: admin
```

Kredensial tersebut hanya digunakan untuk pengujian lokal. Port Codespaces harus tetap Private dan password default perlu diganti untuk deployment sebenarnya.

Untuk membuka dashboard:

```text
Grafana
→ Dashboards
→ TempCast Malang
→ TempCast Malang - ML Observability Dashboard
```

## Scaling Model Serving

Konfigurasi tiga replika pada Docker Compose:

```yaml
deploy:
  replicas: 3
```

Jalankan tiga replika:

```bash
docker compose up -d --no-deps --scale model-serving=3 model-serving
```

Periksa container:

```bash
docker compose ps model-serving
```

Prometheus secara otomatis mendeteksi ketiga replika melalui DNS service discovery.

## Verifikasi Scraping Prometheus

Buka halaman:

```text
http://localhost:9090/targets
```

Target yang dipantau:

```text
cadvisor       : UP
prometheus     : UP
tempcast-api   : UP
tempcast-model : 3/3 UP
```

Verifikasi melalui terminal:

```bash
curl -s http://localhost:9090/api/v1/targets | python -c 'import json,sys; d=json.load(sys.stdin); [print(t["labels"]["job"], "|", t["scrapeUrl"], "|", t["health"]) for t in d["data"]["activeTargets"]]'
```

## Pengujian Endpoint Inference

Pengujian model dilakukan menggunakan endpoint `/invocations`.

```bash
docker compose exec model-serving python -c 'import requests; payload={"dataframe_records":[{"temperature_2m_min":22.0,"temperature_2m_mean":26.0,"precipitation_sum":1.0,"wind_speed_10m_max":12.0,"temperature_2m_max_lag1":30.0,"temperature_2m_max_lag3":29.5,"temperature_2m_max_lag7":30.2,"temperature_2m_max_roll3_mean":29.8,"temperature_2m_max_roll7_mean":30.0,"month":11,"day_of_year":322}]}; r=requests.post("http://localhost:8080/invocations",json=payload); print("Status:",r.status_code); print("Response:",r.text)'
```

Hasil pengujian:

```text
Status: 200
Prediction: 30.543929633198587
```

Hasil prediksi sama dengan pengujian LK-10 untuk input tersebut.

## Metrik yang Dipantau

### Metrik Model Serving

| Metric | Fungsi |
|---|---|
| tempcast_model_requests_total | Jumlah request inference |
| tempcast_model_errors_total | Jumlah kegagalan inference |
| tempcast_model_latency_seconds | Histogram latensi inference |
| tempcast_model_prediction | Histogram hasil prediksi |
| tempcast_model_latest_prediction | Prediksi terakhir setiap replika |
| tempcast_model_ready | Kesiapan model |
| process_cpu_seconds_total | Penggunaan waktu CPU oleh proses |
| process_resident_memory_bytes | Penggunaan resident memory |

### Metrik Data Drift FastAPI

| Metric | Fungsi |
|---|---|
| tempcast_feature_baseline_mean | Rata-rata fitur training |
| tempcast_feature_current_mean | Rata-rata kumulatif input |
| tempcast_feature_drift_score | Pergeseran relatif mean fitur |
| tempcast_feature_drift_detected | Indikator drift setiap fitur |
| tempcast_drift_threshold | Threshold deteksi drift |

## Dashboard Grafana

Dashboard terdiri dari 16 panel:

1. Active Model Replicas
2. Total Successful Requests
3. Inference Error Rate
4. Latest Prediction
5. Inference Latency - p50 and p95
6. Inference Throughput - Requests per Second
7. Traffic Distribution per Replica
8. Prediction Distribution
9. Average Predicted Temperature
10. Inference Error Rate Over Time
11. Model CPU Usage per Replica
12. Model RAM Usage per Replica
13. Input Temperature Mean - Baseline vs Current
14. Data Drift Score per Feature
15. Data Drift Detection Status
16. Drifted Input Features

## Interpretasi Metrik

- Latency p50 menunjukkan estimasi median waktu pemrosesan inference.
- Latency p95 menunjukkan estimasi batas latensi bagi 95% request.
- Throughput menunjukkan jumlah request yang diproses setiap detik.
- Error rate menunjukkan persentase kegagalan inference yang tercatat.
- Prediction distribution menunjukkan distribusi nilai prediksi model.
- Traffic distribution menunjukkan jumlah request pada masing-masing replika.
- CPU usage menunjukkan penggunaan CPU oleh proses model serving.
- RAM usage menunjukkan resident memory proses model serving.
- Drift score menunjukkan besarnya pergeseran mean fitur terhadap baseline.

## Contoh PromQL

Latensi p50 dalam milidetik:

```promql
1000 * histogram_quantile(
  0.50,
  sum by (le) (
    rate(tempcast_model_latency_seconds_bucket[1m])
  )
)
```

Latensi p95 dalam milidetik:

```promql
1000 * histogram_quantile(
  0.95,
  sum by (le) (
    rate(tempcast_model_latency_seconds_bucket[1m])
  )
)
```

Throughput:

```promql
sum(rate(tempcast_model_requests_total[1m]))
```

Error rate:

```promql
100 *
sum(rate(tempcast_model_errors_total[1m]))
/
clamp_min(
  sum(rate(tempcast_model_requests_total[1m])),
  0.000001
)
```

Distribusi trafik setiap replika:

```promql
sum by (replica) (
  rate(tempcast_model_requests_total[1m])
)
```

Replika aktif berdasarkan scraping:

```promql
sum(up{job="tempcast-model"})
```

Jumlah fitur yang mengalami drift:

```promql
sum(tempcast_feature_drift_detected)
```

## Simulasi Beban Kerja

Script simulasi disimpan pada:

```text
src/load_test.py
```

Jalankan:

```bash
docker compose exec -T api-service python - < src/load_test.py
```

Simulasi menggunakan tiga worker dan berjalan selama 180 detik.

Script menemukan alamat IP replika melalui DNS, kemudian mengirimkan variasi input cuaca secara langsung ke masing-masing replika.

Metode ini merupakan simulasi distribusi trafik terkontrol, bukan pengujian load balancing otomatis.

### Hasil Load Testing

| Parameter | Hasil |
|---|---:|
| Durasi | 180 detik |
| Replika aktif | 3 |
| Request berhasil replika 1 | 448 |
| Request berhasil replika 2 | 445 |
| Request berhasil replika 3 | 447 |
| Total request berhasil | 1.340 |
| Total error | 0 |
| Success rate | 100% |
| Error rate | 0% |
| Latency p50 | Sekitar 3 ms |
| Latency p95 | Sekitar 4,8 ms |
| Throughput | Sekitar 7,5 req/s saat pengujian |

Dashboard mencatat total 1.341 request berhasil karena terdapat satu request pengujian awal sebelum simulasi beban kerja.

Distribusi request hampir merata pada ketiga replika.

## Implementasi Data Drift Detection

Deteksi data drift dilakukan pada endpoint FastAPI `/predict` dengan membandingkan rata-rata kumulatif fitur input terhadap baseline yang dihitung dari bagian training dataset.

Rumus:

```text
Drift Score = abs(current_mean - baseline_mean)
              / max(abs(baseline_mean), 0.000001)
```

Threshold drift:

```text
0.15 atau 15%
```

Interpretasi:

- Drift score di bawah 0,15: NORMAL.
- Drift score mencapai atau melebihi 0,15: DRIFT DETECTED.

### Justifikasi Threshold

Threshold 15% digunakan sebagai batas awal eksperimen agar variasi kecil pada nilai input tidak langsung dianggap sebagai drift.

Threshold tersebut bukan batas statistik yang telah divalidasi dan masih dapat disesuaikan berdasarkan karakteristik data, variasi musiman, serta evaluasi model.

Dashboard juga menggunakan threshold error rate sebesar 2% sebagai peringatan visual awal dan 5% sebagai kondisi kritis. Nilai tersebut digunakan sebagai batas eksperimental untuk menandai peningkatan kegagalan layanan, bukan standar SLA yang telah divalidasi.

Indikator warna pada dashboard merupakan peringatan visual. Implementasi ini belum mencakup pengiriman notifikasi alert otomatis.

### Simulasi Kondisi Normal

Script:

```text
src/drift_test.py
```

Jalankan:

```bash
python src/drift_test.py normal
```

Simulasi mengirimkan 60 request dengan variasi input yang mendekati baseline training.

Hasil:

```text
Data Drift Detection Status: NORMAL
Drifted Input Features: 0 dari 11 fitur
```

### Simulasi Kondisi Drift

Setelah menjalankan simulasi normal, jalankan:

```bash
python src/drift_test.py drift
```

Simulasi mengirimkan 120 request dengan pergeseran sintetis sebesar 8 derajat Celsius pada tujuh fitur temperatur.

Hasil:

```text
Data Drift Detection Status: DRIFT DETECTED
Drifted Input Features: 7 dari 11 fitur
```

Pergeseran temperatur tersebut merupakan skenario sintetis untuk menguji mekanisme deteksi, bukan data kejadian cuaca aktual.

### Verifikasi Drift Metrics

```bash
curl -s http://localhost:8000/metrics | grep '^tempcast_feature_drift_score'
```

```bash
curl -s http://localhost:8000/metrics | grep '^tempcast_feature_drift_detected'
```

Dashboard menampilkan perbandingan baseline dan current mean, drift score setiap fitur, threshold, serta jumlah fitur yang mengalami drift.

Pengujian data drift dilakukan melalui FastAPI, sedangkan simulasi trafik model serving dilakukan pada tiga replika MLflow.

Rata-rata input dihitung secara kumulatif sejak API dijalankan. Untuk mengulang eksperimen dari kondisi awal, pastikan MLflow dan PostgreSQL tersedia sebelum melakukan restart FastAPI.

## Analisis Monitoring dan Model Decay

Model machine learning dapat mengalami penurunan performa ketika karakteristik data aktual berbeda dengan karakteristik data training.

Kondisi tersebut dapat terjadi meskipun layanan inference berjalan tanpa error.

Monitoring distribusi prediksi dan statistik fitur input membantu memberikan peringatan awal ketika terjadi perubahan pola data.

Apabila drift terdeteksi, langkah berikutnya dapat berupa:

1. Memeriksa kualitas dan karakteristik data terbaru.
2. Membandingkan distribusi input dengan baseline training.
3. Mengevaluasi model menggunakan nilai aktual.
4. Mengukur MAE, RMSE, dan R2.
5. Menentukan kebutuhan retraining model.

Data drift tidak secara langsung membuktikan terjadinya penurunan akurasi model. Evaluasi terhadap ground truth tetap diperlukan untuk memastikan model decay.

Metode mean shift yang digunakan juga belum mencakup seluruh perubahan distribusi, seperti perubahan varians, korelasi antar-fitur, dan concept drift.

## Optimasi Resource GitHub Codespaces

Pengujian dilakukan menggunakan GitHub Codespaces dengan kapasitas RAM sekitar 8 GB.

MLflow Server menggunakan sumber daya yang cukup besar. Setelah model berhasil dimuat oleh FastAPI dan artifact model tersedia di Docker image, MLflow Server dan PostgreSQL dihentikan sementara untuk mengurangi penggunaan RAM.

```bash
docker compose stop mlflow-server postgres-db
```

Kemudian tiga replika model dijalankan:

```bash
docker compose up -d --no-deps --scale model-serving=3 model-serving
```

FastAPI yang sudah berjalan tetap dapat digunakan untuk inference dan monitoring drift. Kontainer model serving menggunakan artifact model yang tersimpan di dalam image.

FastAPI tidak boleh direstart ketika MLflow Server masih berhenti karena proses startup membutuhkan Model Registry.

Untuk mengaktifkan kembali layanan registry:

```bash
docker compose up -d postgres-db mlflow-server
```

Penggunaan RAM dapat dipantau menggunakan:

```bash
free -h
docker stats --no-stream
```

## Persistent Volumes

Volume yang digunakan:

```text
postgres_data
mlflow_artifacts
prometheus_data
grafana_data
```

Volume digunakan untuk mempertahankan database, artifact model, histori metrik Prometheus, dan data Grafana.

## Menghentikan Sistem

Untuk menghentikan seluruh layanan tanpa menghapus data:

```bash
docker compose stop
```

Untuk menghentikan dan menghapus container serta network:

```bash
docker compose down
```

Hindari menggunakan `docker compose down -v` apabila data dan artifact model masih diperlukan karena opsi tersebut akan menghapus named volume.

## Ringkasan LK-11

Implementasi observability pada TempCast Malang berhasil dilakukan menggunakan Prometheus dan Grafana yang terintegrasi melalui Docker Compose.

Prometheus berhasil melakukan scraping terhadap tiga replika model dengan status 3/3 UP.

Simulasi beban kerja selama 180 detik menghasilkan 1.340 request berhasil tanpa error, dengan distribusi trafik yang hampir merata.

Grafana berhasil menampilkan metrik latensi, throughput, error rate, CPU, RAM, distribusi hasil prediksi, serta statistik fitur input.

Pengujian data drift berhasil menunjukkan perubahan kondisi NORMAL menjadi DRIFT DETECTED dengan tujuh dari sebelas fitur yang melampaui threshold.

Implementasi ini memberikan dasar monitoring operasional dan peringatan awal terhadap potensi model decay untuk mendukung tahapan continuous training berikutnya.

---

Project ini menggunakan MIT License.