class FeatureRegistry:

    def __init__(self):
        self._features = []

    def register(self, feature):
        self._features.append(feature)

    def get_features(self):
        return self._features