from abc import ABC, abstractmethod


class BaseConnector(ABC):
    """
    Base class for all football data connectors.

    Every connector follows the same ETL lifecycle:
    download -> validate -> transform -> save
    """

    def __init__(self, name: str):
        self.name = name

    @abstractmethod
    def download(self):
        pass

    @abstractmethod
    def validate(self):
        pass

    @abstractmethod
    def transform(self):
        pass

    @abstractmethod
    def save(self):
        pass

    def sync(self):
        print(f"\n[{self.name}] Sync started")

        self.download()
        self.validate()
        self.transform()
        self.save()

        print(f"[{self.name}] Sync completed")