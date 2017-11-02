import os
from ArincTypes import Word429, Word708
from enum import IntEnum, unique
from ArincTypes import Rates, Arinc429ParityTypeIn


@unique
class ChannelTypes(IntEnum):
    Unknown = 0
    Arinc429 = 1
    Arinc708 = 2
    Rs232 = 3
    Ftd = 4


class TraceInfo:
    def __init__(self):
        self.label = ""
        self.version = None
        self.date_time = None
        self.channel_type: ChannelTypes = None
        self.parity: Arinc429ParityTypeIn = None
        self.rate: Rates = None
        self.words = []

        self.__show_parse = False

    def import_track(self, path):
        if os.path.isfile(path) is False:
            return None
        file = open(path, "rb")

        # header
        header = file.read(1024)

        offset = 0
        """ Label """

        label = header[0:offset + 14].decode("utf-8")
        self.label = label
        offset = offset + 14

        """ Version """

        version = int.from_bytes(header[offset:offset + 4], byteorder='little')
        self.version = version
        offset = offset + 4

        """ Date time"""

        date_time = int.from_bytes((header[offset:offset + 8]), byteorder='little')
        self.date_time = date_time
        offset = offset + 8

        """ Type """

        channel_type = ChannelTypes(int.from_bytes(header[offset:offset + 4], byteorder='little'))
        self.channel_type = channel_type
        offset = offset + 4
        # channel_type == 0 or channel_type == 3 or channel_type == 4
        if any(channel_type == t for t in [ChannelTypes.Unknown, ChannelTypes.Rs232, ChannelTypes.Ftd]):
            raise (ValueError("Wrong type: {}".format(channel_type.name)))

        if channel_type is ChannelTypes.Arinc429:

            """ Rate """

            rate = Rates(int.from_bytes(header[offset:offset + 4], byteorder='little'))
            self.rate = rate
            offset = offset + 4

            """ Parity """

            parity = Arinc429ParityTypeIn(int.from_bytes(header[offset:offset + 4], byteorder='little'))
            self.parity = parity
            offset = offset + 4

            """ Output """
            if self.__show_parse:
                print(self.__dict__)

            """ Data """

            # data
            file.seek(1024, 1)
            # read 429 data
            counter = 1
            for word429 in words_429_from_raw(file):
                self.words.append(word429)
                if self.__show_parse:
                    print("{}: Data: {}, Time: {}".format(counter, word429.data, word429.time))
                counter = counter + 1
            return True

        if channel_type is ChannelTypes.Arinc708:

            """ Output """
            if self.__show_parse:
                print(self.__dict__)

            """ Data """

            # data
            file.seek(1024, 1)
            # read 708 data
            counter = 1
            for word708 in words_708_from_raw(file):
                self.words.append(word708)
                if self.__show_parse:
                    print("{}: Data: {}, Time: {}".format(counter, word708.data, word708.time))
                counter = counter + 1
            return True


def words_429_from_raw(file):
    while True:
        chunk = file.read(8)
        if chunk:
            tmp_429 = Word429()
            tmp_429.time = int.from_bytes(chunk[:4], byteorder='little')
            tmp_429.data = int.from_bytes(chunk[4:], byteorder='little')
            yield tmp_429
        else:
            break


def words_708_from_raw(file):
    while True:
        chunk = file.read(204)
        if chunk:
            tmp_708 = Word708()
            tmp_708.time = int.from_bytes(chunk[:4], byteorder='little')
            tmp_708.data = int.from_bytes(chunk[4:], byteorder='little')
            yield tmp_708
        else:
            break


