from abc import ABCMeta, abstractmethod
from Generic_Arinc_IO_types.ComplicatedProcess import ComplicatedProcess
from Arinc_IO.TrackParser import TraceInfo


class Sender(ComplicatedProcess, metaclass=ABCMeta):
    def __init__(self):

        super().__init__()

        # List of Arinc words to send
        self._words = []

        # Painter to the list of Arinc words 429
        self.__context = None

        self.__first_pointer = None

        self._dynamic_functor = None

    def _do(self, sharedList=None):
        self.send()

    @abstractmethod
    def _reset_channel(self):
        pass

    @abstractmethod
    def _initialize_context(self):
        pass

    @abstractmethod
    def _setup_channel(self):
        pass

    @abstractmethod
    def send(self):
        pass

    @abstractmethod
    def append(self, data):
        """
        Parse arguments and try to add them in packet
        :param data: list or tuple of word data
        """
        pass

    @abstractmethod
    def _validate_channel_type(self, channel_type):
        pass

    def import_from_file(self, path):
        tr_info = TraceInfo()
        if tr_info.import_track(path) is None:
            raise (IOError("File : \"{}\" is not exist.". format(path)))
        if self._validate_channel_type(tr_info.channel_type) is False:
            raise (ValueError("Wrong channel type: {}".format(tr_info.channel_type.name)))

        self._words = tr_info.words



    def clearWords(self):
        """
        Remove all Arinc words from the packet
        """
        self._words.clear()

    def get_words_count(self):
        """
        :return: count of Arinc words in the packet
        """
        return len(self._words)

    def remove(self, indexStart: int = None, indexEnd: int = None):
        """
        Remove Arinc words by index
        If indexEnd is None remove one word with indexStart if word exist in the packet.
        If indexStart is None remove all words before the indexEnd.
        If indexStart is not None and indexEnd is not None remove all words in this range.
        If indexStart is None and indexEnd is None do nothing.
        :param indexStart:
        :param indexEnd:
        :return: count of words deleted
        """
        prCount = self.get_words_count()
        if indexStart is None and indexEnd is None:
            return 0
        if indexEnd is None and indexStart is not None:
            del self._words[indexStart]
        if indexStart is None and indexEnd is not None:
            del self._words[:indexEnd]
        if indexStart is not None and indexEnd is not None:
            del self._words[indexStart:indexEnd]
        return prCount - self.get_words_count()

    def set_dynamic_function(self, user_defined_functor):
        self._dynamic_functor = user_defined_functor

    def is_dynamic(self):
        return False if self._dynamic_functor is None else True
