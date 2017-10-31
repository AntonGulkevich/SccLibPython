from Generic_Arinc_IO_types.IArinc708 import IArinc708
from Generic_Arinc_IO_types.Listener import Listener
from time import sleep
from Src.ArincTypes import Word708
import Src.MediatorClientWrapper as Proxy
from Src.MediatorClientWrapper import LibError
from ArincTypes import MAX_WORD708_COUNT


class Arinc708Listener(IArinc708, Listener):
    def __init__(self):
        super().__init__()
        # Constants
        self._max708Count = int(MAX_WORD708_COUNT)

    # protected:
    def _initialize_context(self):
        self.__context = (Word708 * self._max708Count)()

    def _setup_channel(self):
        pass

    def _reset_channel(self):
        err = Proxy.ResetIn708Channel(self.get_serial_number(), self.get_channel_number())
        if err < 0:
            raise (LibError("ResetIn708Channel failed", err))

    # public:

    def recv(self, sharedList=None):
        resultRec = Proxy.Receive708WordsRaw(self.get_serial_number(), self.get_channel_number(), self.__context,
                                             self._max708Count)
        if resultRec < 0:
            raise LibError("Receive708WordsRaw failed.", resultRec)

        if resultRec > 0:
            if self.show_function_details is True:
                print("Received 708 Words: {}".format(resultRec))
            for i in range(resultRec):
                a = Word708()
                a.time = self.__context[i].time
                a.data = self.__context[i].data
                sharedList.append(a)
                if self.show_words_details is True:
                    print("Recv:\tdata:", ' '.join(hex(value).ljust(4) for value in a.data), "\n\t\ttime: {}".format(a.time))

        sleep(0.02)

    def get_log(self):
        """
        :return: dict { data : [ count, time ] }
        """
        if len(self._sharedList) > 0:
            temp_list = []
            for w in self._sharedList:
                w_t = Word708()
                w_t.time = w.time
                w_t.data = w.data
                temp_list.append(w_t)
            sum_of_time = 0
            temp_list[0].time = 0
            for i in range(1, len(temp_list)):
                sum_of_time = sum_of_time + temp_list[i].time
                # print("sum_of_time = ", sum_of_time)
                temp_list[i].time = sum_of_time
                # print("_sharedList = ", temp_list[i].time)
            aggregation_dict = {}
            for i in temp_list:
                test_ = tuple(i.data[0:16])
                count = aggregation_dict.get(test_)
                if count is None:
                    aggregation_dict.setdefault(test_, [1, i.time])
                else:
                    new_count = count[0] + 1
                    aggregation_dict.update({test_: [new_count, i.time]})

            return aggregation_dict
        else:
            return None
