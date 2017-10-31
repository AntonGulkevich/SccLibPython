from ArincTypes import Rates


class IArinc429:
    def __init__(self):
        super().__init__()
        # Arinc rate
        self.__rate = None
        # Arinc parity type
        self.__parity = None

    def get_rate(self):
        return self.__rate

    def get_parity(self):
        return self.__parity

    def set_rate(self, rate: Rates):
        self.__rate = rate

    def set_parity(self, parity):
        self.__parity = parity
