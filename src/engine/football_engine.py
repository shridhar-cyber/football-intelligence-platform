from typing import Any, List

from src.engine.connectors.statsbomb_connector import StatsBombConnector
from src.engine.connectors.football_data_connector import (
    FootballDataConnector,
)


class FootballEngine:
    """
    Registers and executes football data connectors.
    """

    def __init__(self, register_defaults: bool = True):
        self.connectors: List[Any] = []

        if register_defaults:
            self.register_default_connectors()

    def register_default_connectors(self) -> None:
        self.add_connector(
            StatsBombConnector(category="international")
        )

        self.add_connector(
            FootballDataConnector()
        )

    def get_connectors(self) -> List[Any]:
        return self.connectors

    def add_connector(self, connector: Any) -> None:
        connector_name = getattr(
            connector,
            "name",
            connector.__class__.__name__,
        )

        already_registered = any(
            getattr(
                existing,
                "name",
                existing.__class__.__name__,
            )
            == connector_name
            for existing in self.connectors
        )

        if already_registered:
            print(f"Connector already registered: {connector_name}")
            return

        self.connectors.append(connector)

    def sync(self) -> None:
        print("\nStarting Football Intelligence Plugin Engine...\n")

        if not self.connectors:
            print("No connectors registered.")
            return

        successful = 0
        failed = 0

        for connector in self.connectors:
            connector_name = getattr(
                connector,
                "name",
                connector.__class__.__name__,
            )

            print(f"Running connector: {connector_name}")

            try:
                connector.sync()
                successful += 1
                print(f"{connector_name}: sync complete\n")

            except Exception as exc:
                failed += 1
                print(f"{connector_name}: sync failed - {exc}\n")

        print("Connector sync summary")
        print(f"Successful: {successful}")
        print(f"Failed: {failed}")

        if failed:
            raise RuntimeError(
                f"{failed} connector(s) failed during synchronization."
            )

        print("\nAll connectors synced successfully!")


if __name__ == "__main__":
    FootballEngine().sync()