from pathlib import Path
import json
import joblib

from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix,
    f1_score,
)

from xgboost import XGBClassifier

from src.models.model_utils import (
    load_dataset,
    FEATURE_COLUMNS,
)

MODEL_DIR = Path("data/models")
MODEL_DIR.mkdir(parents=True, exist_ok=True)


class XGBoostTrainer:

    def train(self):

        X_train, X_test, y_train, y_test = load_dataset()

        numeric = Pipeline([
            ("imputer", SimpleImputer(strategy="median")),
            ("scaler", StandardScaler()),
        ])

        preprocessor = ColumnTransformer([
            ("num", numeric, FEATURE_COLUMNS)
        ])

        model = XGBClassifier(
            objective="multi:softmax",
            num_class=3,
            n_estimators=300,
            learning_rate=0.05,
            max_depth=6,
            subsample=0.8,
            colsample_bytree=0.8,
            random_state=42,
            eval_metric="mlogloss"
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
        print("XGBoost Results")
        print("=" * 50)

        print(f"Accuracy : {accuracy:.4f}")
        print(f"Macro F1 : {macro_f1:.4f}")

        print("\nConfusion Matrix")
        print(confusion_matrix(y_test, preds))

        print("\nClassification Report")
        print(classification_report(y_test, preds))

        joblib.dump(
            pipeline,
            MODEL_DIR / "xgboost.joblib"
        )

        with open(
            MODEL_DIR / "xgboost_metrics.json",
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
    XGBoostTrainer().train()