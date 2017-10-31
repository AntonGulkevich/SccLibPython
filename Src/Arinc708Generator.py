from ctypes import c_byte
from enum import IntEnum
from copy import deepcopy


class ColorIndex(IntEnum):
    black = 0
    green = 1
    yellow = 2
    red = 3
    magenta = 4
    cyan = 5
    white = 6
    gray = 7


class Arinc708Generator:
    def __init__(self):
        # Data field of Arinc708 word
        self.__byteColorsData = bytearray(200)
        self.clear()
        # Template for default data palette
        self.__defaultPalette = [[c_byte(255), c_byte(228), c_byte(196)],
                                 [c_byte(222), c_byte(164), c_byte(135)],
                                 [c_byte(255), c_byte(127), c_byte(80)],
                                 [c_byte(210), c_byte(105), c_byte(30)],
                                 [c_byte(0), c_byte(100), c_byte(0)],
                                 [c_byte(85), c_byte(107), c_byte(47)],
                                 [c_byte(34), c_byte(139), c_byte(34)],
                                 [c_byte(143), c_byte(188), c_byte(143)]]
        # Scale of distance
        self.__scale = 600
        # Color dictionary RGB
        self.__colorDictionary = {
            ColorIndex.black: [c_byte(0), c_byte(0), c_byte(0)],
            ColorIndex.green: [c_byte(0), c_byte(128), c_byte(0)],
            ColorIndex.yellow: [c_byte(255), c_byte(255), c_byte(0)],
            ColorIndex.red: [c_byte(255), c_byte(0), c_byte(0)],
            ColorIndex.magenta: [c_byte(255), c_byte(0), c_byte(255)],
            ColorIndex.cyan: [c_byte(0), c_byte(255), c_byte(255)],
            ColorIndex.white: [c_byte(255), c_byte(255), c_byte(255)],
            ColorIndex.gray: [c_byte(128), c_byte(128), c_byte(128)],
        }

    def fillBitsWithColor(self, fromBit: int, toBit: int, colorIndex: ColorIndex):
        """
        :param fromBit: value must be bigger than 64
        :param toBit:
        :param colorIndex:
        :return: None
        """
        # Set maximum range to the end bit position
        if toBit > 512*3:
            toBit = 512*3

        if toBit <= fromBit or fromBit < 0 or toBit < 0:
            # TODO: Stub to handle toBit position less then fromBit
            raise ValueError("Wrong data: fromBit: {0}, toBit: {1}.".format(fromBit, toBit))

        clrshift = 0
        for bitPos in range(fromBit, toBit):
            tmp = self.__byteColorsData[int(bitPos / 8)]
            self.__byteColorsData[int(bitPos / 8)] = tmp | (colorIndex & (1 << clrshift)) >> clrshift << (bitPos % 8)
            clrshift += 1
            if clrshift == 3:
                clrshift = 0

    def clear(self):
        self.__byteColorsData = bytearray(200)

    def get(self):
        z = bytearray(200)
        z = deepcopy(self.__byteColorsData)
        return z

    def setHeader(self, header: bytearray):
            self.__byteColorsData[:len(header)] = header[:]
