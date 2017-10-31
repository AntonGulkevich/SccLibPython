from abc import ABCMeta, abstractmethod
from multiprocessing import Process, Event, Manager
from time import sleep
from Src import MediatorClientWrapper as Proxy
from Src.MediatorClientWrapper import LibError
from Generic_Arinc_IO_types.IOSettings import IOSettings
from ArincTypes import  Mode


class ComplicatedProcess(IOSettings, metaclass=ABCMeta):
    def __init__(self):
        # ------------------------private-------------------------------------------
        super().__init__()
        # stop signalization
        self.__stop_event = Event()
        # main parallel process
        self.__process = Process()
        # parallel timeout process
        self._timeout_process = Process()
        # period
        self.__period = None
        # flag reset channel before main process
        self.__is_reset = False

    # protected
        manager = Manager()
        self._sharedList = manager.list()

        #  Print flags
        self.show_function_details = False
        self.show_words_details = False

    # protected
    def _on_timeout(self, timeoutMs: int = 0):
        sleep(timeoutMs / 1000)
        self.stop()

    def _complicated_process(self, timeoutMs, sharedList=None):
        # Initialize SCC TCP Mediator
        startupError = Proxy.STMStartupLocal()
        if startupError is not 0:
            raise LibError("STMStartupLocal failed.", startupError)

        if Proxy.IsOnline() is 0:
            sleep(0.5)

        if Proxy.IsOnline() is 0:
            raise LibError("Failed to connect to the server.")

        # Check device
        # if user didn't provide serial number select the first available device
        if self.get_serial_number() is None:
            dev_count = Proxy.GetDeviceCount()
            if dev_count < 0:
                raise LibError("GetDeviceCount failed.", dev_count)
            devices = Proxy.GetDeviceNumsRaw(dev_count)
            if devices[0] < 0:
                raise LibError("GetDeviceNumsRaw failed.", devices)
            self._set_serial_number(devices[0])

        # Setup channel
        self._setup_channel()

        self.__stop_event.clear()

        # if reset buffer flag is set
        if self.__is_reset is True:
            # reset channel
            self._reset_channel()

        # fixme
        sleep(0.02)

        # Start timeout
        self._timeout_process = Process(target=self._on_timeout, args=(timeoutMs,))
        self._timeout_process.start()

        self._initialize_context()

        while not self.__stop_event.is_set():
            # todo cycles?
            self._do(sharedList)

        # reset channel
        self._reset_channel()

        # disconnect
        Proxy.Disconnect()

    # protected abstract
    @abstractmethod
    def _initialize_context(self):
        ...

    @abstractmethod
    def _do(self, sharedList=None):
        ...

    @abstractmethod
    def _reset_channel(self):
        pass

    @abstractmethod
    def _setup_channel(self):
        pass

    # public methods
    def start(self, mode: Mode, timeoutMs: int = 0):
        self.__process = Process(target=self._complicated_process, args=(timeoutMs, self._sharedList))
        self.__process.start()
        if mode is Mode.sync:
            self.__process.join(None if timeoutMs is 0 else timeoutMs / 1000)
            self.stop()

    def stop(self):
        """
        Raise stop event
        """
        self.__stop_event.set()

    def join(self, timeoutMs: int = 0):
        """
        Blocks current process till _do is over or on timeout
        :param timeoutMs: time in milliseconds
        """
        if self.__process.is_alive() is True:
            self.__process.join(None if timeoutMs is 0 else timeoutMs / 1000)
            self.stop()

    def set_reset_buffer_flag(self, is_reset: bool):
        self.__is_reset = is_reset

    def get_reset_buffer_flag(self):
        return self.__is_reset
