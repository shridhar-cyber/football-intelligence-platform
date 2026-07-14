from src.engine.connectors.statsbomb_connector import StatsBombConnector


class FootballEngine:
    def __init__(self, register_defaults=True):
        self.connectors = []

        if register_defaults:
            self.register_default_connectors()

    def register_default_connectors(self):
        self.add_connector(
            StatsBombConnector(category="international")
        )

    def get_connectors(self):
        return self.connectors

    def add_connector(self, connector):
        self.connectors.append(connector)

    def sync(self):
        print("\nStarting Football Intelligence Plugin Engine...\n")

        if not self.connectors:
            print("No connectors registered.")
            return

        for connector in self.connectors:
            connector_name = getattr(
                connector,
                "name",
                connector.__class__.__name__,
            )

            print(f"Running connector: {connector_name}")
            connector.sync()

        print("\nAll connectors synced successfully!")


if __name__ == "__main__":
    FootballEngine().sync()