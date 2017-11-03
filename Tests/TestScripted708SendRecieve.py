from Arinc_IO.Arinc708Sender import Arinc708Sender
from Arinc_IO.Arinc708Listener import Arinc708Listener
import struct
from ctypes import c_ubyte
from ArincTypes import Mode
from Arinc708Generator import Arinc708Generator, ColorIndex


def foo(val):
    tmp = bytearray(val.data)
    print(val.time)
    sh = struct.unpack('@H', tmp[6:8])
    sh = sh[0] + 30
    byteR = struct.pack("H", sh & 0xFFFF)
    tmp[6] = byteR[0]
    tmp[7] = byteR[1]
    val.data = (c_ubyte * 200)(*tmp)
    return val


if __name__ == '__main__':
    # Create header
    header = bytearray.fromhex("03DA17F8010001B4")
    header.reverse()
    # Initialize the Arinc 708 word's data generator
    genInst = Arinc708Generator()
    # Set header
    genInst.setHeader(header)
    # Add colors to the Arinc 708 word's data field
    genInst.fillBitsWithColor(100, 700, ColorIndex.red)
    genInst.fillBitsWithColor(700, 1400, ColorIndex.white)
    # Get the Arinc 708 word's data
    word708Data = genInst.get()

    header = bytearray.fromhex("03DA17F8010001F4")
    header.reverse()
    genInst.setHeader(header)
    genInst.fillBitsWithColor(100, 1500, ColorIndex.magenta)
    word708Data2 = genInst.get()

    # Initialize test environment
    sender708 = Arinc708Sender()
    sender708.setup(500)
    sender708.bind(None, 0)
    sender708.append(word708Data)
    sender708.append(word708Data2)
    sender708.show_function_details = True
    sender708.show_words_details = True
    sender708.start(Mode.async, 5000)

    listener708 = Arinc708Listener()
    listener708.bind(None, 0)
    listener708.set_reset_buffer_flag(True)
    listener708.show_function_details = True
    listener708.show_words_details = True
    listener708.start(Mode.async, 4000)

    listener708.join()
    sender708.join()

    arg_d = listener708.get_log(0, 16)

    print("{0:{1}^86}".format(" Log 708", "="))
    for key, value in arg_d.items():
        # if key & 0xff == 3:
        print("data: ", ' '.join(hex(d).ljust(4) for d in key), "\ncount: ", value[0], "\ntime: ", value[1])