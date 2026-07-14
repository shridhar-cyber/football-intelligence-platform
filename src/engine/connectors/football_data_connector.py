class FootballDataConnector:
    name = "football-data"

    def __init__(self):
        self.downloaded_data = None
        self.processed_data = None

    def download(self):
        print("[Football-Data] Downloading league datasets...")

    def validate(self):
        print("[Football-Data] Validating data...")

    def transform(self):
        print("[Football-Data] Transforming matches...")

    def save(self):
        print("[Football-Data] Saving processed data...")

    def sync(self):
        print(f"\n[{self.name}] Sync started")

        self.download()
        self.validate()
        self.transform()
        self.save()

        print(f"[{self.name}] Sync completed")