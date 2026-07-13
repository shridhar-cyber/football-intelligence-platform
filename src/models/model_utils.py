from pathlib import Path
import pandas as pd

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

DATASET_PATH = Path("data/features/training_dataset.csv")


def load_dataset():
    df = pd.read_csv(DATASET_PATH)

    df["match_date"] = pd.to_datetime(df["match_date"])

    df = df.sort_values("match_date").reset_index(drop=True)

    split = int(len(df) * 0.8)

    train = df.iloc[:split]
    test = df.iloc[split:]

    X_train = train[FEATURE_COLUMNS]
    y_train = train[TARGET_COLUMN]

    X_test = test[FEATURE_COLUMNS]
    y_test = test[TARGET_COLUMN]

    return X_train, X_test, y_train, y_test