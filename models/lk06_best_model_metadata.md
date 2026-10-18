# LK-06 Best Model Metadata

## Model Information
- Project: TempCast Malang
- Experiment: TempCast-Malang-LK06-Final
- Best Run: linear_regression_baseline
- Model Type: LinearRegression

## Dataset and Training
- Dataset Source: Dataset versioned pada LK-05 menggunakan DVC
- Train/Test Split: 80:20 secara kronologis
- Training Rows: 444
- Testing Rows: 111
- Feature Count: 11

## Evaluation Metrics
- MAE: 0.8297
- RMSE: 1.0349
- R2: 0.4549

## Model Selection
Linear Regression dipilih sebagai model terbaik karena menghasilkan MAE dan RMSE
paling rendah serta R2 paling tinggi dibandingkan tiga konfigurasi Random Forest
yang diuji pada eksperimen LK-06.

## MLflow Registry
- Registered Model: TempCast-Malang-Best-Model
- Version: 1
- Model Artifact: model
- Serialization Format: cloudpickle

## Deployment Readiness
Model ini dipilih sebagai kandidat untuk tahap model packaging dan deployment
pada milestone berikutnya.
