from src.engine.connectors.statsbomb_connector import StatsBombConnector


class FootballEngine:
    def __init__(self):
        self.connectors = []

    def add_connector(self, connector):
        self.connectors.append(connector)

    def sync(self):
        print("\nStarting Football Intelligence Plugin Engine...\n")

        for connector in self.connectors:
            print(f"Running connector: {connector.name}")
            connector.sync()

        print("\nAll connectors synced successfully!")


if __name__ == "__main__":
    engine = FootballEngine()
    engine.add_connector(StatsBombConnector(category="international"))
    engine.sync()