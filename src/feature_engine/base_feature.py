from abc import ABC, abstractmethod


class BaseFeature(ABC):
    """
    Base class for all football feature modules.
    """

    @abstractmethod
    def compute(self, context):
        pass