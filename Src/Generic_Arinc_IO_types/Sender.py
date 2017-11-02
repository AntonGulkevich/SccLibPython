from abc import ABCMeta, abstractmethod
from Generic_Arinc_IO_types.ComplicatedProcess import ComplicatedProcess
from Arinc_IO.TrackParser import TrackInfo


class Sender(ComplicatedProcess, metaclass=ABCMeta):
    def __init__(self):

        super().__init__()

        # List of Arinc words to send
        self._words = []

        # Painter to the list of Arinc words 429
        self.__context = None

        self.__first_pointer = None

        self._dynamic_functor = None

        self._track_info: TrackInfo = None

        self.__is_imported = False

        self._imported_words_sent = 0

    def is_imported(self):
        return self.__is_imported

    def _do(self, sharedList=None):
        if self.is_imported():
            self.send_imported()
        else:
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
    def send_imported(self):
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

    @abstractmethod
    def _import_settings(self):
        pass

    def import_from_file(self, path):
        self.__is_imported = True
        # clear dynamic functor
        self._dynamic_functor = None
        # init track info
        self._track_info = TrackInfo()
        # import track from file
        if self._track_info.import_track(path) is None:
            raise (IOError("File : \"{}\" is not exist.". format(path)))
        # ensure we are working with correct channel type
        if self._validate_channel_type(self._track_info.channel_type) is False:
            raise (ValueError("Wrong channel type: {}".format(self._track_info.channel_type.name)))
        # import settings
        self._import_settings()

    def clearWords(self):
        """
        Remove all Arinc words from the packet
        """
        if self.is_imported():
            return self._track_info.words.clear()
        else:
            self._words.clear()

    def get_words_count(self):
        """
        :return: count of Arinc words in the packet
        """
        if self.is_imported():
            return len(self._track_info.words)
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
        if self.is_imported():
            raise (ImportError("Data was imported. \"{}\" function is unavailable in import mode.".format(self.remove.__name__)))

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
        if self.is_imported():
            raise (ImportError("Data was imported. \"{}\" function is unavailable in import mode.".format(self.set_dynamic_function.__name__)))
        self._dynamic_functor = user_defined_functor

    def is_dynamic(self):
        return self._dynamic_functor is not None
