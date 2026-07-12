from src.feature_engine.feature_engine import FeatureEngine


def test_feature_engine_output():
    engine = FeatureEngine()

    features = engine.build(
        home_team="Brazil",
        away_team="Argentina",
        last_n_matches=5,
    )

    required_features = [
        "home_recent_form",
        "away_recent_form",
        "recent_form_difference",
        "home_avg_goals_scored",
        "away_avg_goals_scored",
        "home_avg_goals_conceded",
        "away_avg_goals_conceded",
        "head_to_head_matches",
        "home_h2h_win_rate",
        "away_h2h_win_rate",
        "home_home_form",
        "away_away_form",
        "home_away_form_difference",
    ]

    for feature_name in required_features:
        assert feature_name in features, f"Missing feature: {feature_name}"

    numeric_features = [
        value for value in features.values()
        if isinstance(value, (int, float))
    ]

    assert numeric_features, "No numeric features were generated"

    for value in numeric_features:
        assert value is not None

    print("Feature Engine validation passed.")
    print(f"Total features generated: {len(features)}")


if __name__ == "__main__":
    test_feature_engine_output()