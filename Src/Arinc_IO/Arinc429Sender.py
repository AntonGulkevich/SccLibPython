from Generic_Arinc_IO_types.IArinc429 import IArinc429
from Generic_Arinc_IO_types.Sender import Sender
from time import sleep
from Src.ArincTypes import Word429
from ctypes import c_ulong, byref
import Src.MediatorClientWrapper as Proxy
from Src.MediatorClientWrapper import LibError
from ArincTypes import Rates, Arinc429ParityTypeOut, RateTimes, MAX_WORD429_COUNT
import copy
from Arinc_IO.TrackParser import ChannelTypes


class Arinc429Sender(IArinc429, Sender):
    def __init__(self):
        super().__init__()

        self.__is_first = True

    # private:
    def __add_new_word_429(self, data: int):
        if len(self._words) == MAX_WORD429_COUNT:
            raise LibError("__add_new_word_429 failed. Buffer overflow. Maximum of Arinc  429 words count: {}.".format(MAX_WORD429_COUNT))
        if (self.__periodMs is None
            or self.get_channel_number() is None
            or self.get_rate() is None
            or self.get_parity() is None):
            # if one of required parameters is not set
            raise LibError("Setup parameters before adding data. Rate {}. Period {}. Channel number {}. Parity {}."
                           .format(self.get_rate(), self.__periodMs, self.get_channel_number(), self.get_parity()))

        dataChunkTimeMs = (len(self._words) + 1) * self.get_rate() / 100
        if dataChunkTimeMs > self.__periodMs:
            raise ValueError("Critical error: Total Data chunk time if bigger than period!\n"
                             "Word429 count: {0}. Rate: {1}. Total time: {2} ms. Period: {3} ms."
                             .format(len(self._words) + 1, self.get_rate(), dataChunkTimeMs, self.__periodMs))
        w = Word429()
        w.data = c_ulong(data)
        w.time = RateTimes[self.get_rate()]
        self._words.append(w)

        self._words[0].time = self.__periodMs * 100 - (len(self._words) - 1) * RateTimes[self.get_rate()]

    # protected:
    def _validate_channel_type(self, channel_type):
        return ChannelTypes.Arinc429 == channel_type

    def _initialize_context(self):
        if self.is_imported():
            return
        else:
            self.__context = byref((Word429 * len(self._words))(*self._words))

            _f_words = copy.deepcopy(self._words)
            _f_words[0].time = RateTimes[self.get_rate()]
            self.__first_pointer = byref((Word429 * len(_f_words))(*_f_words))

    def _setup_channel(self):
        err = Proxy.Set429OutputChannelParams(self.get_serial_number(), self.get_channel_number(), self.get_rate(),
                                              self.get_parity())
        if err == 0 and self.show_function_details is True:
            print("Set 429 Output Channel Params is OK.")
        if err < 0:
            raise LibError("Unable to set output channel parameters of 429 channel.", err)

    def _reset_channel(self):
        err = Proxy.ResetOut429Channel(self.get_serial_number(), self.get_channel_number())
        if err == 0 and self.show_function_details is True:
            print("Reset Out 429 Channel is OK")
        if err < 0:
            raise (LibError("ResetOut429Channel failed", err))

    def _import_settings(self):
        if self._track_info.rate is None:
            raise ValueError("Failed to import channel's rate from file.")
        if self._track_info.parity is None:
            raise ValueError("Failed to import channel's parity from file.")
        self.set_rate(self._track_info.rate)
        self.set_parity(self._track_info.parity)

    # public:
    def setup(self, rate: Rates, parity: Arinc429ParityTypeOut, periodMs: int):
        self.set_rate(rate)
        self.set_parity(parity)
        self.__periodMs = periodMs

    def append(self, *data):
        for elem in data:
            if isinstance(elem, int):
                self.__add_new_word_429(elem)
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

    def send_imported(self):
        words_count_to_send = len(self._track_info.words) - self._imported_words_sent
        if words_count_to_send > 0:
            words_prepared_to_send = words_count_to_send if words_count_to_send < MAX_WORD429_COUNT else MAX_WORD429_COUNT
            # print(words_count_to_send, " Max ", MAX_WORD429_COUNT, " prepared:", words_prepared_to_send)
            tmp_buf = []
            for w in self._track_info.words[self._imported_words_sent:words_prepared_to_send+self._imported_words_sent]:
                word = Word429()
                word.data = w.data
                word.time = w.time
                tmp_buf.append(word)
            self.__context = byref((Word429 * words_prepared_to_send)(*tmp_buf))

            sendRec = Proxy.Send429WordsRaw(self.get_serial_number(), self.get_channel_number(), self.__context,
                                            words_prepared_to_send)
            if sendRec < 0:
                raise LibError("Send429WordsRaw failed. ", sendRec)

            if sendRec > 0 and self.show_function_details is True:
                print("Sent 429 words: {}".format(sendRec))

            if sendRec > 0 and self.show_words_details is True:
                for w in tmp_buf:
                    print("Sent:  data: {:10} time: {}".format(hex(w.data), w.time))

            self._imported_words_sent = self._imported_words_sent + words_prepared_to_send
        else:
            res_count = Proxy.Get429OutputBufferWordsCount(self.get_serial_number(), self.get_channel_number())
            if res_count == 0:
                self._imported_words_sent = 0

        sleep(0.02)

    def send(self):
        res_mcs = Proxy.Get429OutputBufferMicroseconds(self.get_serial_number(), self.get_channel_number())
        # print("res_mcs = {}".format(res_mcs))
        if res_mcs < 0:
            raise LibError("Get429OutputBufferMicroseconds failed.", res_mcs)

        doublePeriodMicroseconds = 2 * 1000 * self.__periodMs

        if doublePeriodMicroseconds > res_mcs >= 0:
            if self.__is_first is True:
                sendRec = Proxy.Send429WordsRaw(self.get_serial_number(), self.get_channel_number(),
                                                self.__first_pointer,
                                                len(self._words))
            else:
                if self.is_dynamic() is True:
                    for w in self._words:
                        w.data = self._dynamic_functor(w.data)
                    self.__context = byref((Word429 * len(self._words))(*self._words))
                sendRec = Proxy.Send429WordsRaw(self.get_serial_number(), self.get_channel_number(), self.__context,
                                                len(self._words))

            if sendRec < 0:
                raise LibError("Send429WordsRaw failed.", sendRec)

            if sendRec > 0 and self.show_function_details is True:
                print("Sent 429 words: {}".format(sendRec))

            if sendRec > 0 and self.show_words_details is True:
                for w in self._words:
                    print("Sent:  data: {:10} time: {}".format(hex(w.data), w.time if self.__is_first is False else RateTimes[self.get_rate()]))
            self.__is_first = False
        sleep(0.02)
