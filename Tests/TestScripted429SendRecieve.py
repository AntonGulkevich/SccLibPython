from Arinc_IO.Arinc429Sender import Arinc429Sender
from Arinc_IO.Arinc429Listener import Arinc429Listener
from ArincTypes import Arinc429ParityTypeOut, Arinc429ParityTypeIn, Rates, Mode


def inc(data):
    return data + 1


if __name__ == '__main__':

    sender429 = Arinc429Sender()
    sender429.setup(Rates.R100, Arinc429ParityTypeOut.NoChange, 200)
    sender429.bind(None, 2)
    sender429.append(1, 44, 2, 3, [44, 55, 66], 11, 3735929054)
    sender429.set_dynamic_function(inc)
    sender429.show_function_details = True
    sender429.show_words_details = True
    sender429.start(Mode.async, 4000)

    listener429 = Arinc429Listener()
    listener429.setup(Rates.R100, Arinc429ParityTypeIn.NoChange)
    listener429.bind(None, 2)
    listener429.set_reset_buffer_flag(True)
    listener429.show_function_details = True
    listener429.show_words_details = True
    listener429.start(Mode.async, 5000)

    listener429.join()
    sender429.join()

    arg_d = listener429.get_log()

    print("{0:{1}^86}".format(" Log 429", "="))
    for key, value in arg_d.items():
        # if key & 0xff == 3:
        print("data: {} count: {}\tthe last time: {}".format(hex(key).ljust(max(len(hex(i)) for i, v in arg_d.items())), value[0], value[1]))