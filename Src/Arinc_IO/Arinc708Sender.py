from Generic_Arinc_IO_types.IArinc708 import IArinc708
from Generic_Arinc_IO_types.Sender import Sender
import Src.MediatorClientWrapper as Proxy
from Src.MediatorClientWrapper import LibError
from ctypes import byref, c_ubyte
from Src.ArincTypes import Word708, MAX_WORD708_COUNT
import copy
from time import sleep


class Arinc708Sender(IArinc708, Sender):
    def __init__(self):
        super().__init__()
        self.__is_first = True
        self.__rate_time = 166

    # public:
    def setup(self, periodMs: int):
        self.__periodMs = periodMs

    def send(self):
        res_mcs = Proxy.Get708OutputBufferMicroseconds(self.get_serial_number(), self.get_channel_number())
        # print("res_mcs = {}".format(res_mcs))
        if res_mcs < 0:
            raise LibError("Get708OutputBufferMicroseconds failed.", res_mcs)

        doublePeriodMicroseconds = 2 * 1000 * self.__periodMs

        if doublePeriodMicroseconds > res_mcs >= 0:
            if self.__is_first is True:
                sendRec = Proxy.Send708WordsRaw(self.get_serial_number(), self.get_channel_number(),
                                                self.__first_pointer,
                                                len(self._words))
            else:
                if self.is_dynamic() is True:
                    for w in self._words:
                        w.data = self._dynamic_functor(w.data)
                    # self._words[:] = map(self._dynamic_functor, self._words)
                    self.__context = byref((Word708 * len(self._words))(*self._words))
                sendRec = Proxy.Send708WordsRaw(self.get_serial_number(), self.get_channel_number(), self.__context,
                                                len(self._words))

            if sendRec < 0:
                raise LibError("Send708WordsRaw failed.", sendRec)

            if sendRec > 0 and self.show_function_details is True:
                print("Send 708 words: {}".format(sendRec))

            if sendRec > 0 and self.show_words_details is True:
                for w in self._words:
                    print(self.__is_first)
                    print("Sent:\tdata:", ' '.join(hex(value).ljust(4) for value in w.data),
                          "\n\t\ttime: {}".format(w.time if self.__is_first is False else self.__rate_time))
            self.__is_first = False
        sleep(0.02)

    def append(self, *data):
        for elem in data:
            if isinstance(elem, bytearray):
                if len(elem) == 200:
                    self.__add_new_word_708(elem)
                    continue
            if isinstance(elem, list):
                for i in elem:
                    self.append(i)
                continue
            if isinstance(elem, tuple):
                for i in elem:
                    self.append(i)
                continue
            raise ValueError("Undefined data: {0}".format(elem))

    # protected:
    def _reset_channel(self):
        err = Proxy.ResetOut708Channel(self.get_serial_number(), self.get_channel_number())
        if err < 0:
            raise (LibError("ResetOut708Channel failed", err))

    def _initialize_context(self):
        self.__context = byref((Word708 * len(self._words))(*self._words))
        _f_words = copy.deepcopy(self._words)
        _f_words[0].time = self.__rate_time
        self.__first_pointer = byref((Word708 * len(_f_words))(*_f_words))

    def _setup_channel(self):
        # no need to setup channel
        pass

    def _apply_user_defined_dynamic(self):
        pass

    # private:
    def __add_new_word_708(self, data: bytearray):
        if len(self._words) == MAX_WORD708_COUNT:
            raise LibError("__add_new_word_708 failed. Buffer overflow. Maximum of Arinc 708 words count: {}.".format(MAX_WORD708_COUNT))

        if self.__periodMs is None or self.get_channel_number() is None:
            # if one of required parameters is not set
            raise LibError("Setup parameters before adding data. Period {}. Channel number {}. "
                           .format(self.__periodMs, self.get_channel_number()))

        dataChunkTimeMs = (len(self._words) + 1) * self.__rate_time / 100
        if dataChunkTimeMs > self.__periodMs:
            raise ValueError("Critical error: Total Data chunk time if bigger than period!\n"
                             "Word708 count: {0}. Rate: {1}. Total time: {2} ms. Period: {3} ms."
                             .format(len(self._words) + 1, self.__rate_time, dataChunkTimeMs, self.__periodMs))
        w = Word708()
        w.data = (c_ubyte * 200)(*data)
        w.time = self.__rate_time
        self._words.append(w)

        self._words[0].time = self.__periodMs * 100 - (len(self._words) - 1) * self.__rate_time
