## LK-09 - Docker Compose Orchestration

LK-09 mengorkestrasi sistem TempCast Malang menggunakan Docker Compose dengan tiga layanan utama:

- `api-service`: FastAPI untuk inferensi model.
- `mlflow-server`: MLflow Tracking Server dan Model Registry.
- `postgres-db`: PostgreSQL sebagai backend metadata MLflow.

Seluruh layanan berjalan pada custom bridge network `tempcast-network` sehingga antar-container dapat saling berkomunikasi menggunakan nama service.

Persistent storage menggunakan:

- `postgres_data` untuk database PostgreSQL.
- `mlflow_artifacts` untuk artefak MLflow.

### Menjalankan Sistem

Seluruh sistem dapat dijalankan dengan satu perintah:

```bash
docker compose up -d --build
