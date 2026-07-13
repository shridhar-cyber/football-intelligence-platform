import pandas as pd


class DataValidator:

    def __init__(self, dataset_path):
        self.df = pd.read_csv(dataset_path)

    def validate(self):
        print("=" * 50)
        print("DATASET SUMMARY")
        print("=" * 50)

        print(f"Rows: {len(self.df)}")
        print(f"Columns: {len(self.df.columns)}")

        print("\nColumns:")
        print(self.df.columns.tolist())

        print("\nMissing Values")
        print(self.df.isnull().sum())

        print("\nDuplicate Rows")
        print(self.df.duplicated().sum())

        print("\nTarget Distribution")
        print(self.df["target"].value_counts())

        print("\nFeature Statistics")
        print(self.df.describe())

        print("\nValidation Complete")


if __name__ == "__main__":
    validator = DataValidator("data/features/training_dataset.csv")
    validator.validate()