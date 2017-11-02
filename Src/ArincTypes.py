import ctypes
from enum import IntEnum


class Mode(IntEnum):
    sync = 0
    async = 1


class Word429(ctypes.Structure):
    _fields_ = [('time', ctypes.c_ulong),
                ('data', ctypes.c_ulong)]


class Word708(ctypes.Structure):
    _fields_ = [('time', ctypes.c_ulong),
                ('data', ctypes.c_ubyte * 200)]


class Rates(IntEnum):
    Disabled = 0
    R12_5 = 1
    R50 = 2
    R100 = 3


class Arinc429ParityTypeOut(IntEnum):
    NoChange = 0
    Even = 1
    Odd = 2
    Always0 = 3
    Always1 = 4


class Arinc429ParityTypeIn(IntEnum):
    NoChange = 0
    Analysis = 1


RateTimes = {Rates.Disabled: 0, Rates.R100: 36, Rates.R50: 72, Rates.R12_5: 288}

# define MAX_BUFFER_LEN (0x1000 * 30)
MAX_BUFFER_LEN = 0x1000 * 30
# define HEADER_LENGTH (3 * sizeof(UINT))
HEADER_LENGTH = 3 * 4
# define MAX_WORD429_COUNT ((MAX_BUFFER_LEN/sizeof(Word429)) - HEADER_LENGTH)
MAX_WORD429_COUNT = int(MAX_BUFFER_LEN / 8 - HEADER_LENGTH)
# define MAX_WORD708_COUNT ((MAX_BUFFER_LEN/sizeof(Word708)) - HEADER_LENGTH)
MAX_WORD708_COUNT = int(MAX_BUFFER_LEN / 204 - HEADER_LENGTH)
