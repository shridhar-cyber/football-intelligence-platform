from pathlib import Path

import joblib
import matplotlib.pyplot as plt
import pandas as pd


MODEL_PATH = Path(
    "artifacts/trained_models/lightgbm.joblib"
)

OUTPUT_DIR = Path(
    "artifacts/feature_importance"
)

OUTPUT_DIR.mkdir(
    parents=True,
    exist_ok=True,
)


def main():
    print("Loading model...")

    pipeline = joblib.load(MODEL_PATH)

    preprocessor = pipeline.named_steps["preprocessor"]
    lightgbm_model = pipeline.named_steps["model"]

    feature_names = preprocessor.get_feature_names_out()

    # Remove prefixes such as "numeric__"
    cleaned_feature_names = [
        name.split("__", 1)[-1]
        for name in feature_names
    ]

    feature_importances = (
        lightgbm_model.feature_importances_
    )

    if len(cleaned_feature_names) != len(feature_importances):
        raise ValueError(
            "Feature-name and importance counts do not match: "
            f"{len(cleaned_feature_names)} names vs "
            f"{len(feature_importances)} importance values."
        )

    importance = pd.DataFrame(
        {
            "feature": cleaned_feature_names,
            "importance": feature_importances,
        }
    )

    importance = (
        importance
        .sort_values(
            "importance",
            ascending=False,
        )
        .reset_index(drop=True)
    )

    print("\nTop Features\n")
    print(importance.to_string(index=False))

    csv_path = (
        OUTPUT_DIR / "feature_importance.csv"
    )

    image_path = (
        OUTPUT_DIR / "feature_importance.png"
    )

    importance.to_csv(
        csv_path,
        index=False,
    )

    plt.figure(figsize=(10, 7))

    plt.barh(
        importance["feature"],
        importance["importance"],
    )

    plt.gca().invert_yaxis()
    plt.xlabel("Importance")
    plt.ylabel("Feature")
    plt.title("LightGBM Feature Importance")
    plt.tight_layout()

    plt.savefig(
        image_path,
        dpi=300,
        bbox_inches="tight",
    )

    plt.close()

    print(f"\nSaved: {csv_path}")
    print(f"Saved: {image_path}")


if __name__ == "__main__":
    main()