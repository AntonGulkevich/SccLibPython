from abc import ABCMeta, abstractmethod
from Generic_Arinc_IO_types.ComplicatedProcess import ComplicatedProcess


class Listener(ComplicatedProcess, metaclass=ABCMeta):
    def __init__(self):

        super().__init__()

        # List of Arinc words to receive
        self._words = []

        # Painter to the list of Arinc words 429
        self.__context = None

    def _do(self, sharedList=None):
        self.recv(sharedList)

    @abstractmethod
    def _reset_channel(self):
        pass

    @abstractmethod
    def _initialize_context(self):
        pass

    @abstractmethod
    def _setup_channel(self):
        pass

    @abstractmethod
    def recv(self):
        pass
