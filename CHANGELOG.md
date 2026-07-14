# Changelog

All notable changes to the Football Intelligence Platform are documented here.

---

# Sprint 1 — Data Ingestion Engine

## Added
- Created modular football data ingestion framework.
- Integrated StatsBomb connector.
- Competition configuration system.
- Automatic competition filtering by category.
- Downloaded competitions, seasons and match datasets.
- Data validation pipeline.
- Raw and processed data separation.

## Result
- Successfully downloaded 333 international matches.
- Created reusable connector architecture.

---

# Sprint 2 — Football Warehouse

## Added
- Designed SQLite football warehouse.
- Created normalized database schema.
- Warehouse initialization service.
- Competition repository.
- Season repository.
- Team repository.
- Match repository.

## Result
Warehouse successfully stores:

- 24 Competitions
- 80 Seasons
- 78 Teams
- 333 Matches

---

# Sprint 3 — Repository Layer

## Added
Repository methods for:

- Get all matches
- Get matches by team
- Last N matches
- Head-to-head history
- Home matches
- Away matches

## Result
Feature engineering can now access historical data efficiently.

---

# Sprint 4 — Feature Engineering Engine

## Added

### Recent Form
- Recent points
- Recent form score

### Goal Statistics
- Average goals scored
- Average goals conceded
- Clean sheet rate
- Scoring rate

### Head-to-Head
- Previous meetings
- Win counts
- Draw count
- Goal difference

### Home / Away Form
- Home-only performance
- Away-only performance
- Venue-specific goal statistics

## Result
Generated 28+ football intelligence features.

---

# Sprint 5 — Machine Learning Pipeline

## Added

Training pipeline for

- Logistic Regression
- Random Forest
- XGBoost
- LightGBM

## Added

- Model evaluation
- Confusion Matrix
- Classification Report
- Accuracy
- Macro F1
- Model serialization
- Metrics serialization

## Initial Results

| Model | Accuracy |
|--------|----------|
| Logistic Regression | 36.07% |
| Random Forest | 36.07% |
| XGBoost | 34.43% |
| LightGBM | 39.34% |

LightGBM selected as baseline production model.

---

# Sprint 6 — Project Architecture Improvements

## Added

- Feature Registry
- Artifact directory
- Model output separation

Repository structure improved.

Generated files moved to

artifacts/

instead of

data/

---

# Sprint 7 — Football Intelligence Layer

## Added

### Elo Repository

- Dynamic team ratings

### Elo Feature

Generated

- Home Elo
- Away Elo
- Elo Difference

### Historical Elo Builder

Implemented leakage-free Elo generation for historical matches.

Each match now stores

- Pre-match Home Elo
- Pre-match Away Elo

before ratings are updated.

## Result

Historical dataset created

Rows

302

Columns

17

---

# Sprint 7.5 — Live Data Pipeline

## Added

LiveDataService

Automatic workflow

StatsBomb
↓

Validation
↓

Registry Generation
↓

Warehouse Refresh

One command now performs the complete pipeline

python -m src.services.live_data_service

## Warehouse Verification

Successfully refreshes

- Competitions
- Seasons
- Teams
- Matches

Pipeline now supports future scheduled execution.

---

# Current Project Status

## Completed

✅ Modular Connector Framework

✅ Football Warehouse

✅ Repository Layer

✅ Feature Engineering Engine

✅ Historical Feature Generation

✅ Machine Learning Pipeline

✅ LightGBM Baseline

✅ Live Data Refresh Pipeline

---

# Upcoming

Sprint 8

- Football-Data Connector
- Expanded historical dataset
- Warehouse merge

Sprint 9

- Feature engineering improvements
- Model retraining
- Feature importance

Sprint 10

- Prediction API

Sprint 11

- AI Football Analyst (RAG)

Sprint 12

- Streamlit Dashboard

Sprint 13

- Production Deployment