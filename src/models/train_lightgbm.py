from pathlib import Path
import json
import joblib

from lightgbm import LGBMClassifier

from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix,
    f1_score,
)
from sklearn.pipeline import Pipeline

from src.models.model_utils import (
    FEATURE_COLUMNS,
    load_dataset,
)


MODEL_DIR = Path("artifacts/trained_models")
METRICS_DIR = Path("artifacts/metrics")

MODEL_DIR.mkdir(parents=True, exist_ok=True)
METRICS_DIR.mkdir(parents=True, exist_ok=True)


class LightGBMTrainer:
    def train(self):
        X_train, X_test, y_train, y_test = load_dataset()

        preprocessor = ColumnTransformer(
            transformers=[
                (
                    "numeric",
                    SimpleImputer(strategy="median"),
                    FEATURE_COLUMNS,
                )
            ]
        )

        model = LGBMClassifier(
            objective="multiclass",
            num_class=3,
            n_estimators=300,
            learning_rate=0.05,
            max_depth=6,
            num_leaves=31,
            subsample=0.8,
            colsample_bytree=0.8,
            class_weight="balanced",
            random_state=42,
            verbosity=-1,
        )

        pipeline = Pipeline(
            steps=[
                ("preprocessor", preprocessor),
                ("model", model),
            ]
        )

        pipeline.fit(X_train, y_train)

        predictions = pipeline.predict(X_test)

        accuracy = accuracy_score(y_test, predictions)
        macro_f1 = f1_score(
            y_test,
            predictions,
            average="macro",
            zero_division=0,
        )

        matrix = confusion_matrix(
            y_test,
            predictions,
            labels=[0, 1, 2],
        )

        print("=" * 50)
        print("LightGBM Results")
        print("=" * 50)
        print(f"Accuracy : {accuracy:.4f}")
        print(f"Macro F1 : {macro_f1:.4f}")

        print("\nConfusion Matrix")
        print(matrix)

        print("\nClassification Report")
        print(
            classification_report(
                y_test,
                predictions,
                zero_division=0,
            )
        )

        model_path = MODEL_DIR / "lightgbm.joblib"
        metrics_path = METRICS_DIR / "lightgbm_metrics.json"

        joblib.dump(pipeline, model_path)

        metrics = {
            "model": "LightGBM",
            "accuracy": round(float(accuracy), 4),
            "macro_f1": round(float(macro_f1), 4),
            "confusion_matrix": matrix.tolist(),
        }

        with open(metrics_path, "w", encoding="utf-8") as file:
            json.dump(metrics, file, indent=4)

        print(f"\nModel saved at: {model_path}")
        print(f"Metrics saved at: {metrics_path}")


if __name__ == "__main__":
    LightGBMTrainer().train()