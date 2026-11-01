# TempCast Malang — MLOps Project

## Deskripsi

TempCast Malang adalah prototipe akademik untuk memprediksi suhu maksimum harian Kota Malang satu hari ke depan (`t+1`) menggunakan pendekatan supervised time-series regression.

Project ini dikembangkan secara bertahap untuk menerapkan konsep MLOps, mulai dari setup environment, data ingestion dinamis, preprocessing, hingga data versioning menggunakan DVC.

Pada LK-04, project telah mengimplementasikan dynamic data ingestion dan preprocessing.

Pada LK-05, project dikembangkan lebih lanjut dengan integrasi Data Version Control (DVC) untuk melakukan versioning dataset, mencatat perubahan data, serta mendukung reproducibility dan audit data pada skenario continual learning.

## Tujuan Proyek

Project ini dirancang untuk:

- menggunakan data cuaca harian Kota Malang,
- memprediksi suhu maksimum hari berikutnya,
- menggunakan Open-Meteo Historical Weather API sebagai sumber data,
- mengambil data secara dinamis dan berkala,
- melakukan preprocessing data secara konsisten,
- melakukan versioning dataset menggunakan DVC,
- menjaga reproducibility dan data lineage dalam pipeline MLOps.

## Struktur Direktori

```text
MLOps-TempCast-Malang/
├── .devcontainer/
│   └── devcontainer.json
├── .dvc/
│   ├── .gitignore
│   └── config
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
│   ├── hello.py
│   ├── ingest_data.py
│   ├── main.py
│   └── preprocess.py
├── tests/
│   └── test_smoke.py
├── .dvcignore
├── .gitignore
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

## LK-04: Dynamic Data Ingestion

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

Dataset awal yang digunakan untuk LK-05 memiliki:

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

## LK-05: Manajemen Data Versioning Menggunakan DVC

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

Perubahan hash menunjukkan bahwa isi dataset telah berubah.

Perbandingan file metadata `.dvc` juga dapat dilihat menggunakan:

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

Untuk mendemonstrasikan mekanisme remote storage, digunakan local DVC remote.

Remote dibuat menggunakan:

```bash
mkdir -p ../dvc-storage
dvc remote add -d localremote ../dvc-storage
```

Konfigurasi pada `.dvc/config`:

```text
[core]
    remote = localremote

['remote "localremote"']
    url = ../../dvc-storage
```

Data DVC dikirim ke remote menggunakan:

```bash
dvc push
```

Hasil:

```text
1 file pushed
```

Pengecekan semua versi:

```bash
dvc push --all-commits
```

Hasil:

```text
Everything is up to date.
```

Local remote digunakan sebagai simulasi mekanisme remote storage.

Pada implementasi production, remote dapat diganti menggunakan object storage seperti:

- AWS S3,
- Google Cloud Storage,
- MinIO,
- Azure Blob Storage.

## Data Lineage

Histori perubahan dataset dapat ditelusuri melalui kombinasi Git dan DVC.

Histori utama LK-05:

```text
bc40083 chore: configure DVC remote storage
8151a3f data: update LK5 dataset to version 2
76533cd data: track initial LK5 dataset with DVC
e5586f9 chore: initialize DVC for LK5
```

Dengan mekanisme ini, dapat diketahui:

- kapan DVC mulai digunakan,
- versi dataset awal,
- kapan dataset diperbarui,
- hash setiap versi,
- perubahan ukuran dataset,
- konfigurasi remote storage.

## Mengapa Data Versioning Penting?

Data versioning merupakan bagian penting dalam MLOps karena model machine learning sangat bergantung pada data yang digunakan saat training.

Jika dataset berubah tanpa pencatatan versi, hasil eksperimen akan sulit direproduksi.

Sebagai contoh, model yang dilatih menggunakan Dataset Versi 1 dapat menghasilkan performa berbeda dengan model yang dilatih menggunakan Dataset Versi 2.

Dengan DVC, setiap eksperimen dapat dikaitkan dengan versi dataset tertentu.

Manfaat utama data versioning:

- menjaga reproducibility eksperimen,
- mempermudah audit perubahan data,
- mencatat data lineage,
- membantu debugging,
- mencegah kehilangan histori dataset,
- mendukung continual learning,
- mempermudah kolaborasi tim.

## Git dan DVC

Git digunakan untuk menyimpan:

```text
source code
README
konfigurasi
file .dvc
metadata
```

DVC digunakan untuk mengelola:

```text
dataset
artefak data
cache
remote data storage
```

Dengan pemisahan tersebut, repository Git tetap ringan meskipun dataset berkembang.

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

## Branch LK-05

Implementasi LK-05 dikembangkan pada branch:

```text
experiment/lk5-dvc-versioning
```

Repository:

```text
https://github.com/alyaarhm/MLOps-TempCast-Malang
```

## Kesimpulan

Implementasi LK-05 menunjukkan bahwa DVC dapat digunakan untuk melakukan versioning dataset pada pipeline MLOps TempCast Malang.

Dataset awal sebanyak 550 baris berhasil direkam sebagai Versi 1.

Setelah simulasi penambahan data, dataset berkembang menjadi 563 baris dan direkam sebagai Versi 2.

Perubahan versi dapat dibuktikan melalui perubahan hash DVC, `dvc status`, `git diff`, dan `dvc diff`.

Penggunaan DVC membuat perubahan data dapat ditelusuri dan mendukung reproducibility, audit data, serta continual learning.

## License

Project ini menggunakan MIT License.
## LK-07 - Model Registry, Versioning, dan Kesiapan Inferensi

Pada LK-07, model terbaik dari LK-06 dikelola menggunakan MLflow Model Registry untuk mendukung versioning dan kesiapan inferensi.

### Model Versioning

Model terdaftar menggunakan nama:

`TempCast-Malang-Best-Model`

Versi yang tersedia:

| Version | Model | Feature Count | MAE | RMSE | R2 | Stage |
|---|---|---:|---:|---:|---:|---|
| v1 | Linear Regression | 11 | 0.8297 | 1.0349 | 0.4549 | None |
| v2 | Linear Regression | 12 | 0.8113 | 1.0107 | 0.4801 | Production |

Model v2 menggunakan satu fitur tambahan, yaitu `temperature_2m_max`, sehingga jumlah fitur berubah dari 11 menjadi 12.

### Active Production Model

Model yang aktif untuk inferensi adalah:

- Registered Model: `TempCast-Malang-Best-Model`
- Version: `2`
- Stage: `Production`
- Run: `linear_regression_v2_extra_current_temp`

Version 2 dipilih sebagai model Production karena menghasilkan performa yang lebih baik dibandingkan version 1, yaitu MAE dan RMSE yang lebih rendah serta R2 yang lebih tinggi.

### Model Lifecycle

Transisi stage yang dilakukan pada version 2:

`None -> Staging -> Production`

Transisi ini digunakan untuk mensimulasikan alur pengelolaan model dari hasil eksperimen hingga model siap digunakan untuk inferensi.

### Data Lineage

Model Production tetap terhubung dengan dataset yang telah dikelola menggunakan DVC pada LK-05.

- Dataset: `data/raw/weather_2025-03-20_to_2026-09-20_20260927_224435.csv`
- Dataset Version: `LK05_V2`
- DVC MD5: `24049e0aa0e75db53f723b4833037b93`
- Metadata Model: `models/lk07_production_model.yaml`

### Inference Verification

Model Production berhasil dimuat secara programatik menggunakan:

`mlflow.pyfunc.load_model("models:/TempCast-Malang-Best-Model/Production")`

Pengujian menggunakan satu input baru dengan 12 fitur menghasilkan prediksi:

`30.71120928`

Hal ini menunjukkan bahwa model berstatus Production telah siap dipanggil oleh layanan inferensi pada tahap berikutnya.
