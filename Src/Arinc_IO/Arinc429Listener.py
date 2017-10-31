from Generic_Arinc_IO_types.IArinc429 import IArinc429
from Generic_Arinc_IO_types.Listener import Listener
from time import sleep
from Src.ArincTypes import Word429
import Src.MediatorClientWrapper as Proxy
from Src.MediatorClientWrapper import LibError
from ArincTypes import Rates, Arinc429ParityTypeIn, MAX_WORD429_COUNT


class Arinc429Listener(IArinc429, Listener):
    def __init__(self):
        super().__init__()
        # Constants
        self._max429Count = int(MAX_WORD429_COUNT)

    # protected:
    def _initialize_context(self):
        self.__context = (Word429 * self._max429Count)()

    def _setup_channel(self):
        err = Proxy.Set429InputChannelParams(self.get_serial_number(), self.get_channel_number(), self.get_rate(),
                                             self.get_parity())
        if err < 0:
            raise LibError("Unable to set input channel parameters of 429 channel.", err)

    def _reset_channel(self):
        err = Proxy.ResetIn429Channel(self.get_serial_number(), self.get_channel_number())
        if err < 0:
            raise (LibError("ResetIn429Channel failed", err))

    # public:
    def setup(self, rate: Rates, parity: Arinc429ParityTypeIn):
        self.set_rate(rate)
        self.set_parity(parity)

    def recv(self, sharedList=None):
        resultRec = Proxy.Receive429WordsRaw(self.get_serial_number(), self.get_channel_number(), self.__context,
                                             self._max429Count)
        if resultRec < 0:
            raise LibError("Receive429WordsRaw failed.", resultRec)

        if resultRec > 0:
            if self.show_function_details is True:
                print("Receive429WordsRaw {}\twords.".format(resultRec))
            for i in range(resultRec):
                a = Word429()
                a.time = self.__context[i].time
                a.data = self.__context[i].data
                sharedList.append(a)
                if self.show_words_details is True:
                    print("Recv:  data: {:10} time: {}".format(hex(a.data), a.time))
        sleep(0.02)

    def get_log(self):
        if len(self._sharedList) > 0:
            temp_list = []
            for w in self._sharedList:
                w_t = Word429()
                w_t.time = w.time
                w_t.data = w.data
                temp_list.append(w_t)
            sum_of_time = 0
            temp_list[0].time = 0
            for i in range(1, len(temp_list)):
                sum_of_time = sum_of_time + temp_list[i].time
                temp_list[i].time = sum_of_time

            aggregation_dict = {}
            for i in temp_list:
                count = aggregation_dict.get(i.data)
                if count is None:
                    aggregation_dict.setdefault(i.data, [1, i.time])
                else:
                    new_count = count[0] + 1
                    aggregation_dict.update({i.data: [new_count, i.time]})

            return aggregation_dict
        else:
            return None

    def test_delete_this(self):
        for i in self._sharedList:
            print(type(i.data).__name__, ": ", i.data, type(i.time).__name__, ": ", i.time)
