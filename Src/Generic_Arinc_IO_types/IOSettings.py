class IOSettings:
    def __init__(self):
        # Device serial number
        self.__serial_number = None
        # Channel number
        self.__channel_number = None
        # Period between packets
        self.__periodMs = None

    def bind(self, serial_number: int, channel_number: int):
        self.__serial_number = serial_number
        self.__channel_number = channel_number

    def get_serial_number(self):
        return self.__serial_number

    def get_channel_number(self):
        return self.__channel_number

    def _set_serial_number(self, serial_number: int):
        self.__serial_number = serial_number
