from typing import Any, Iterable

from src.engine.football_engine import FootballEngine
from src.services.warehouse_service import WarehouseService


class LiveDataService:
    """
    Refreshes connector data and then rebuilds the football warehouse.
    """

    def __init__(self):
        self.engine = FootballEngine()
        self.warehouse_service = WarehouseService()

    def run_connectors(self) -> None:
        connectors: Iterable[Any] = self.engine.get_connectors()

        print(f"Registered connectors: {len(connectors)}")

        if not connectors:
            raise RuntimeError("No connectors are registered.")

        failed_connectors = []

        for connector in connectors:
            connector_name = getattr(
                connector,
                "name",
                connector.__class__.__name__,
            )

            print(f"\nRunning connector: {connector_name}")

            try:
                connector.sync()
                print(f"{connector_name}: sync complete")

            except Exception as exc:
                failed_connectors.append(connector_name)
                print(f"{connector_name}: failed - {exc}")

        if failed_connectors:
            raise RuntimeError(
                "Connector refresh failed for: "
                + ", ".join(failed_connectors)
            )

    def refresh_warehouse(self) -> None:
        print("\nRefreshing football warehouse...\n")
        self.warehouse_service.run()
        print("\nFootball warehouse refresh complete.")

    def run(self) -> None:
        print("\nStarting live football-data pipeline...\n")

        self.run_connectors()
        self.refresh_warehouse()

        print("\nLive football-data pipeline completed successfully.")


if __name__ == "__main__":
    LiveDataService().run()