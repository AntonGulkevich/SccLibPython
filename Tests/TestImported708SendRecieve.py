from Arinc_IO.Arinc708Sender import Arinc708Sender
from Arinc_IO.Arinc708Listener import Arinc708Listener
from ArincTypes import Mode
import os


if __name__ == '__main__':

    # маршрут3_процедура.scc429
    # маршрут3_процедура_маневр.scc429
    # path_to_bin = os.path.abspath(os.path.join(os.path.dirname(__file__), '../bin trace//маршрут3_процедура.scc429'))

    path_to_bin = None

    # Initialize test environment

    sender708 = Arinc708Sender()
    sender708.setup(500)
    sender708.bind(None, 0)
    sender708.import_from_file(path_to_bin)
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