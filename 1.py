import pandas as pd

df = pd.read_csv("data/warehouse/seasons.csv")

print(df.head())
print(df.columns)

print("\nTotal rows:", len(df))

print("\nDuplicate season_id:")
print(df[df.duplicated(subset=["season_id"], keep=False)])