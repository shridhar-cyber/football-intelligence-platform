from pathlib import Path
import json
import joblib
import pandas as pd

from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix,
    f1_score,
)
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler


DATASET_PATH = Path("data/features/training_dataset.csv")
MODEL_DIR = Path("data/models")
MODEL_DIR.mkdir(parents=True, exist_ok=True)

MODEL_PATH = MODEL_DIR / "baseline_logistic_regression.joblib"
METRICS_PATH = MODEL_DIR / "baseline_metrics.json"


FEATURE_COLUMNS = [
    "home_form",
    "away_form",
    "form_difference",
    "home_avg_goals_scored",
    "away_avg_goals_scored",
    "home_avg_goals_conceded",
    "away_avg_goals_conceded",
    "home_win_rate",
    "away_win_rate",
]

TARGET_COLUMN = "target"


class BaselineTrainer:
    def __init__(self):
        if not DATASET_PATH.exists():
            raise FileNotFoundError(
                "training_dataset.csv not found. "
                "Run training_dataset_builder first."
            )

        self.df = pd.read_csv(DATASET_PATH)

    def prepare_data(self):
        required_columns = FEATURE_COLUMNS + [
            TARGET_COLUMN,
            "match_date",
        ]

        missing_columns = [
            column
            for column in required_columns
            if column not in self.df.columns
        ]

        if missing_columns:
            raise ValueError(
                f"Dataset is missing columns: {missing_columns}"
            )

        self.df["match_date"] = pd.to_datetime(
            self.df["match_date"],
            errors="coerce",
        )

        self.df = (
            self.df
            .dropna(subset=["match_date", TARGET_COLUMN])
            .sort_values("match_date")
            .reset_index(drop=True)
        )

        if len(self.df) < 20:
            raise ValueError(
                "Not enough training rows. "
                "At least 20 matches are recommended."
            )

        split_index = int(len(self.df) * 0.80)

        train_df = self.df.iloc[:split_index]
        test_df = self.df.iloc[split_index:]

        X_train = train_df[FEATURE_COLUMNS]
        y_train = train_df[TARGET_COLUMN]

        X_test = test_df[FEATURE_COLUMNS]
        y_test = test_df[TARGET_COLUMN]

        return X_train, X_test, y_train, y_test

    def build_pipeline(self):
        numeric_transformer = Pipeline(
            steps=[
                (
                    "imputer",
                    SimpleImputer(strategy="median"),
                ),
                (
                    "scaler",
                    StandardScaler(),
                ),
            ]
        )

        preprocessor = ColumnTransformer(
            transformers=[
                (
                    "numeric",
                    numeric_transformer,
                    FEATURE_COLUMNS,
                )
            ]
        )

        model = LogisticRegression(
            max_iter=2000,
            class_weight="balanced",
            random_state=42,
        )

        return Pipeline(
            steps=[
                ("preprocessor", preprocessor),
                ("model", model),
            ]
        )

    def train(self):
        X_train, X_test, y_train, y_test = self.prepare_data()

        pipeline = self.build_pipeline()
        pipeline.fit(X_train, y_train)

        predictions = pipeline.predict(X_test)

        accuracy = accuracy_score(y_test, predictions)
        macro_f1 = f1_score(
            y_test,
            predictions,
            average="macro",
            zero_division=0,
        )

        report = classification_report(
            y_test,
            predictions,
            output_dict=True,
            zero_division=0,
        )

        matrix = confusion_matrix(
            y_test,
            predictions,
            labels=[0, 1, 2],
        ).tolist()

        metrics = {
            "model": "LogisticRegression",
            "train_rows": len(X_train),
            "test_rows": len(X_test),
            "features": FEATURE_COLUMNS,
            "accuracy": round(float(accuracy), 4),
            "macro_f1": round(float(macro_f1), 4),
            "confusion_matrix": matrix,
            "classification_report": report,
            "class_mapping": {
                "0": "home_win",
                "1": "draw",
                "2": "away_win",
            },
        }

        joblib.dump(pipeline, MODEL_PATH)

        with open(METRICS_PATH, "w", encoding="utf-8") as file:
            json.dump(metrics, file, indent=4)

        print("\nBaseline model trained successfully.")
        print(f"Training rows: {len(X_train)}")
        print(f"Testing rows: {len(X_test)}")
        print(f"Accuracy: {accuracy:.4f}")
        print(f"Macro F1: {macro_f1:.4f}")
        print("\nConfusion Matrix:")
        print(matrix)
        print(f"\nModel saved at: {MODEL_PATH}")
        print(f"Metrics saved at: {METRICS_PATH}")

        return pipeline, metrics


if __name__ == "__main__":
    BaselineTrainer().train()