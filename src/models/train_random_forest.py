from pathlib import Path
import json
import joblib

from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix,
    f1_score,
)

from src.models.model_utils import (
    load_dataset,
    FEATURE_COLUMNS,
)

MODEL_DIR = Path("artifacts/trained_models")
METRICS_DIR = Path("artifacts/metrics")

MODEL_DIR.mkdir(parents=True, exist_ok=True)
METRICS_DIR.mkdir(parents=True, exist_ok=True)


class RandomForestTrainer:

    def train(self):

        X_train, X_test, y_train, y_test = load_dataset()

        numeric = Pipeline([
            ("imputer", SimpleImputer(strategy="median")),
            ("scaler", StandardScaler()),
        ])

        preprocessor = ColumnTransformer([
            ("num", numeric, FEATURE_COLUMNS)
        ])

        model = RandomForestClassifier(
            n_estimators=300,
            max_depth=10,
            random_state=42,
            class_weight="balanced"
        )

        pipeline = Pipeline([
            ("preprocessor", preprocessor),
            ("model", model),
        ])

        pipeline.fit(X_train, y_train)

        preds = pipeline.predict(X_test)

        accuracy = accuracy_score(y_test, preds)
        macro_f1 = f1_score(
            y_test,
            preds,
            average="macro"
        )

        print("=" * 50)
        print("Random Forest Results")
        print("=" * 50)

        print(f"Accuracy : {accuracy:.4f}")
        print(f"Macro F1 : {macro_f1:.4f}")

        print("\nConfusion Matrix")
        print(confusion_matrix(y_test, preds))

        print("\nClassification Report")
        print(classification_report(y_test, preds))

        joblib.dump(
            pipeline,
            MODEL_DIR / "random_forest.joblib"
        )

        with open(
            METRICS_DIR / "random_forest_metrics.json",
            "w"
        ) as f:

            json.dump(
                {
                    "accuracy": accuracy,
                    "macro_f1": macro_f1,
                },
                f,
                indent=4,
            )


if __name__ == "__main__":
    RandomForestTrainer().train()