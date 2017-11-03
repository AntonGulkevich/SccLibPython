from Arinc_IO.Arinc429Sender import Arinc429Sender
from Arinc_IO.Arinc429Listener import Arinc429Listener
from ArincTypes import Arinc429ParityTypeOut, Arinc429ParityTypeIn, Rates, Mode
import os


if __name__ == '__main__':

    # маршрут3_процедура.scc429
    # маршрут3_процедура_маневр.scc429
    path_to_bin = os.path.abspath(os.path.join(os.path.dirname(__file__), '../bin trace//маршрут3_процедура.scc429'))

    sender429_imported = Arinc429Sender()
    sender429_imported.import_from_file(path_to_bin)
    sender429_imported.bind(None, 0)
    sender429_imported.show_function_details = True
    sender429_imported.show_words_details = False
    sender429_imported.start(Mode.async, 5000)

    listener429 = Arinc429Listener()
    listener429.setup(Rates.R100, Arinc429ParityTypeIn.NoChange)
    listener429.bind(None, 0)
    listener429.set_reset_buffer_flag(True)
    listener429.show_function_details = True
    listener429.show_words_details = True
    listener429.start(Mode.async, 5000)

    listener429.join()
    sender429_imported.join()

    arg_d = listener429.get_log()

    print("{0:{1}^86}".format(" Log 429", "="))
    for key, value in arg_d.items():
        # if key & 0xff == 3:
        print("data: {} count: {}\tthe last time: {}".format(hex(key).ljust(max(len(hex(i)) for i, v in arg_d.items())), value[0], value[1]))