from ArincTypes import Arinc429ParityTypeOut, Arinc429ParityTypeIn, Rates, Mode
import struct
from ctypes import c_ubyte
from Arinc_IO.Arinc708Sender import Arinc708Sender
from Arinc_IO.Arinc708Listener import Arinc708Listener
from Arinc_IO.Arinc429Sender import Arinc429Sender
from Arinc_IO.Arinc429Listener import Arinc429Listener
from Arinc708Generator import Arinc708Generator, ColorIndex
from Arinc_IO.xml import Waypoint, import_waypoints_from_xml
import os

# here = lambda x: os.path.abspath(os.path.join(os.path.dirname(__file__), x))
# DATA_DIR = here('datadir')


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


def inc(data):
    return data + 1


if __name__ == '__main__':
    # маршрут3_процедура.scc429
    # маршрут3_процедура_маневр.scc429
    path_to_bin = os.path.abspath(os.path.join(os.path.dirname(__file__), '../bin trace//маршрут3_процедура.scc429'))

    sender429_imported = Arinc429Sender()
    sender429_imported.import_from_file(path_to_bin)
    sender429_imported.bind(None, 0)
    sender429_imported.show_function_details = True
    sender429_imported.show_words_details = False
    sender429_imported.start(Mode.async, 100000)
    sender429_imported.join()

    # path_to_xml = os.path.abspath(os.path.join(os.path.dirname(__file__), '../bin trace//ТочкидляРЛО.xml'))
    # waypoints = import_waypoints_from_xml(path_to_xml)
    #
    # if waypoints is not None:
    #     for wp in waypoints:
    #         print("Waypoint: ")
    #         print(wp.__dict__)

    test708 = False
    test429 = False

    if test708 is True:
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

        arg_d = listener708.get_log()

        print("{0:{1}^86}".format(" Log 708", "="))
        for key, value in arg_d.items():
            # if key & 0xff == 3:
            print("data: ", ' '.join(hex(d).ljust(4) for d in key), "\ncount: ", value[0], "\ntime: ", value[1])
    if test429 is True:
        is_sender_1 = True
        is_sender_2 = False
        is_listener1 = True

        sender429 = Arinc429Sender()
        w_sender429 = Arinc429Sender()

        listener429 = Arinc429Listener()

        if is_listener1 is True:
            listener429.setup(Rates.R100, Arinc429ParityTypeIn.NoChange)
            listener429.bind(None, 2)
            listener429.set_reset_buffer_flag(True)
            listener429.show_function_details = True
            listener429.show_words_details = True
            listener429.start(Mode.async, 5000)

        if is_sender_1 is True:
            sender429.setup(Rates.R100, Arinc429ParityTypeOut.NoChange, 200)
            sender429.bind(None, 2)
            sender429.append(1, 44, 2, 3, [44, 55, 66], 11, 3735929054)
            sender429.set_dynamic_function(inc)
            sender429.show_function_details = True
            sender429.show_words_details = True
            sender429.start(Mode.async, 4000)

        if is_sender_2 is True:
            w_sender429.setup(Rates.R100, Arinc429ParityTypeOut.NoChange, 500)
            w_sender429.bind(None, 2)
            w_sender429.append(1, 44, 2, 3 + 256, [44, 55, 66], 11, 3735929054)
            w_sender429.start(Mode.async, 4000)

        if is_listener1 is True:
            listener429.join()
        if is_sender_1 is True:
            sender429.join()
        if is_sender_2 is True:
            w_sender429.join()

        arg_d = listener429.get_log()

        print("{0:{1}^86}".format(" Log 429", "="))
        for key, value in arg_d.items():
            # if key & 0xff == 3:
            print("data: {} count: {}\tthe last time: {}".format(hex(key).ljust(max(len(hex(i)) for i, v in arg_d.items())), value[0], value[1]))
