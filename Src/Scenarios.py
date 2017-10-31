from Src.ArincTypes import Rates as ArincRate, Word429, Word708, Arinc429ParityTypeOut as ArincParity, RateTimes
from enum import IntEnum
from ctypes import c_ulong, byref, c_ubyte, c_int64
import Src.MediatorClientWrapper as Proxy
from multiprocessing import Process, Event, Manager
from time import sleep
from abc import ABCMeta, abstractmethod


class DeviceError(Exception):
    def __init__(self, message):
        self.message = message
        super().__init__(message)


class LibError(Exception):
    def __init__(self, message):
        self.message = "SCC TCP Mediator: " + message
        super().__init__(self.message)


class Mode(IntEnum):
    sync = 0
    async = 1


class Settings(metaclass=ABCMeta):
    def __init__(self, serialNumber, channelNumber, periodMs, cycles=None):

        # ------------------------public-------------------------------------------

        # Device serial number
        self.serialNumber = serialNumber
        # Channel number
        self.channelNumber = channelNumber
        # Period
        self.periodMS = periodMs
        # Cycle count
        self.cycles = cycles

        # ------------------------protected---------------------------------------

        # Words data implemented with list of data filed
        self._wordsData = []

        # Constants
        self._max429Count = 128
        self._max708Count = 20

        # Multiprocessing
        # Send
        self._stopSendingEvent = Event()
        self._prRec = Process()
        self._timeoutSend = Process()
        # Receive
        self._stopReceivingEvent = Event()
        self._prSend = Process()
        self._timeoutRec = Process()

        # Received data
        self._receivedData = []

        manager = Manager()
        self._sharedList = manager.list()

    @abstractmethod
    def append(self, data):
        """
        Parse arguments and try to add them in packet
        :param data: list or tuple of word data
        """
        pass

    @abstractmethod
    def send(self, timeoutMs: int):
        pass

    @abstractmethod
    def createPacket(self):
        pass

    def clearWords(self):
        """
        Remove all Arinc words from the packet
        """
        self._wordsData.clear()

    @staticmethod
    def _initLib():
        if Proxy.STMStartupLocal() is not 1:
            raise LibError("Initialization failed.")

        if Proxy.IsOnline() is 0:
            sleep(0.5)

        if Proxy.IsOnline() is 0:
            raise LibError("Connection failed.")

    def _checkDeviceState(self):
        dev_count = Proxy.GetDeviceCount()
        if dev_count < 0:
            raise LibError("Can't retrieve device information.")
        if dev_count is 0:
            raise DeviceError("No device available.")
        devices = Proxy.GetDeviceNumsRaw(dev_count)
        # if user didn't provide serial number
        # select the first available one
        if self.serialNumber is None:
            self.serialNumber = devices[0]
        else:
            if self.serialNumber not in devices:
                raise DeviceError("Oh my God! Your device with serial number(%d) is not available. We are so sad ಥ_ಥ\n"
                                  "But its OK! We have %d devices well working right here.\n"
                                  "For example, you can pick one with Serial Number:%d"
                                  % (self.serialNumber, len(devices), devices[0]))

    @abstractmethod
    def _recv(self, sharedList, timeoutMs):
        pass

    def count(self):
        """
        :return: count of Arinc words in the packet
        """
        return len(self._wordsData)

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
        prCount = self.count()
        if indexStart is None and indexEnd is None:
            return 0
        if indexEnd is None and indexStart is not None:
            del self._wordsData[indexStart]
        if indexStart is None and indexEnd is not None:
            del self._wordsData[:indexEnd]
        if indexStart is not None and indexEnd is not None:
            del self._wordsData[indexStart:indexEnd]
        return prCount-self.count()

    def startSending(self, mode: Mode, timeoutMs: int = None):
        """If mode is async, make sure process witch called
           startSending429 won't stop before sending words ends.
           Using join() will block main process till sending words is over."""
        self._prSend = Process(target=self.send, args=(timeoutMs,))
        self._prSend.start()
        if mode is Mode.sync:
            self._prSend.join(None if timeoutMs is 0 else timeoutMs / 1000)
            self.stopSending()

    def listen(self, mode: Mode, timeoutMs: int = None, ):
        self._prRec = Process(target=self._recv, args=(self._sharedList, timeoutMs,))
        self._prRec.start()
        if mode is Mode.sync:
            self._prRec.join(None if timeoutMs is 0 else timeoutMs / 1000)
            self.stopReceiving()

    def stopSending(self):
        """
        Immediately stops sending thread
        """
        if self._stopSendingEvent.is_set() is False:
            self._stopSendingEvent.set()

    def stopReceiving(self):
        """
        Immediately stops receiving thread
        """
        if self._stopReceivingEvent.is_set() is False:
            self._stopReceivingEvent.set()

    def _stopSendingEx(self, timeoutMs: int):
        sleep(timeoutMs / 1000)
        self.stopSending()

    def _stopReceivingEx(self, timeoutMs: int):
        sleep(timeoutMs / 1000)
        self.stopReceiving()

    def joinSend(self, timeoutMs: int = None):
        """
        Blocks current process till send is over or on timeout
        :param timeoutMs: time in milliseconds
        """
        if self._prSend.is_alive() is True:
            if timeoutMs is None:
                self._prSend.join()
            else:
                self._prSend.join(timeoutMs / 1000)
            self.stopSending()

    def joinListen(self, timeoutMs: int = None):
        """
        Blocks current process till send is over or on timeout
        :param timeoutMs: time in milliseconds
        """
        if self._prRec.is_alive() is True:
            if timeoutMs is None:
                self._prRec.join()
            else:
                self._prRec.join(timeoutMs / 1000)
            self.stopReceiving()


class Settings429(Settings):
    def __init__(self, serialNumber, channelNumber, rate: ArincRate, parity: ArincParity, periodMs, cycles=None):
        super(Settings429, self).__init__(serialNumber, channelNumber, periodMs, cycles)
        # Arinc rate
        self.rate = rate
        # Arinc parity type
        self.parity = parity
        # List of Arinc429 words
        self.__words429 = []
        # 429 word with calculated time
        self.__calculatedTimeWord429 = Word429()

    def printReceivedResult(self):
        tmpList = list(x.data for x in self._sharedList)
        return dict((data, [tmpList.count(data), "last time"]) for data in tmpList)

    def _recv(self, sharedList, timeoutMs):
        # Initialize SCC TCP Mediator
        self._initLib()

        # Check device availability
        self._checkDeviceState()

        # Setup channel
        if Proxy.Set429InputChannelParams(self.serialNumber, self.channelNumber, self.rate, self.parity) is not 0:
            raise LibError("Unable to set output channel parameters of 429 channel.")

        # Init timer
        if timeoutMs is not None:
            self._timeoutRec = Process(target=self._stopReceivingEx, args=(timeoutMs,))
            self._timeoutRec.start()

        # Receiving cycle
        currentCycle = 0
        words429 = (Word429 * self._max429Count)()
        self._stopReceivingEvent.clear()
        while not self._stopReceivingEvent.is_set():
            if self.cycles is not None:
                if currentCycle > self.cycles:
                    break
            resultRec = Proxy.Receive429WordsRaw(self.serialNumber, self.channelNumber, words429, self._max429Count)

            if resultRec < 0:
                raise LibError("Receive429WordsRaw failed.")
            if resultRec > 0:
                for i in range(resultRec):
                    a = Word429()
                    a.time = words429[i].time
                    a.data = words429[i].data
                    sharedList.append(a)
                    print(a.data, " ", a.time)
            sleep(0.2)
        Proxy.ResetIn429Channel(self.serialNumber, self.channelNumber)
        Proxy.Disconnect()

    def append(self, data):
        if isinstance(data, int):
            self._wordsData.append(data)
            return
        if isinstance(data, list):
            for i in data:
                self.append(i)
            return
        raise ValueError("Undefined data: {0}".format(data))

    def createPacket(self):
        self.__words429.clear()
        dataChunkTimeMs = len(self._wordsData) * self.rate / 100
        if dataChunkTimeMs > self.periodMS:
            raise ValueError("Critical error: Total Data chunk time if bigger than period!\n"
                             "Word429 count: {0}. Rate: {1}. Total time: {2} ms. Period: {3} ms."
                             .format(len(self._wordsData), self.rate, dataChunkTimeMs, self.periodMS))
        for wordData in self._wordsData:
            w = Word429()
            w.data = c_ulong(wordData)
            w.time = 0
            self.__words429.append(w)

        self.__calculatedTimeWord429.data = self._wordsData[0]
        self.__calculatedTimeWord429.time = self.periodMS * 100 - (len(self.__words429) - 1) * RateTimes[self.rate]

    def send(self, timeoutMs: int):
        # Initialize SCC TCP Mediator
        self._initLib()

        # Check device availability
        self._checkDeviceState()

        # Setup channel
        if Proxy.Set429OutputChannelParams(self.serialNumber, self.channelNumber, self.rate, self.parity) is not 0:
            raise LibError("Unable to set output channel parameters of 429 channel.")

        self.createPacket()

        # Initialize raw data array
        wordsRawFirst = (Word429 * len(self.__words429))(*self.__words429)
        # Create timeout to raise stop event
        if timeoutMs is not None:
            self._timeoutSend = Process(target=self._stopSendingEx, args=(timeoutMs,))
            self._timeoutSend.start()

        doublePeriodMicroseconds = 2 * 1000 * self.periodMS
        currentCycle = 1
        self._stopSendingEvent.clear()
        while not self._stopSendingEvent.is_set():
            if self.cycles is not None:
                if currentCycle > self.cycles:
                    break
            outputBufferMicroseconds = Proxy.Get429OutputBufferMicroseconds(self.serialNumber, self.channelNumber)
            if outputBufferMicroseconds < 0:
                raise LibError("outputBufferMicroseconds failed.")
            if doublePeriodMicroseconds > outputBufferMicroseconds >= 0:

                sendRec = Proxy.Send429WordsRaw(self.serialNumber, self.channelNumber, byref(wordsRawFirst),
                                                len(self._wordsData))
                if sendRec < 0:
                    raise LibError("Send429WordsRaw failed.")
                if currentCycle is 1:
                    self.__words429[0] = self.__calculatedTimeWord429
                    wordsRawFirst = (Word429 * len(self.__words429))(*self.__words429)
                # trace
                # print("Cycle: %d, sent %d Words429." % (currentCycle, sendRec if sendRec >= 0 else 0))
                currentCycle += 1
            sleep(0.02)
        Proxy.ResetOut429Channel(self.serialNumber, self.channelNumber)
        Proxy.Disconnect()


class Settings708(Settings):
    def __init__(self, serialNumber, channelNumber, periodMs):
        super(Settings708, self).__init__(serialNumber, channelNumber, periodMs)
        # Packet data represented by list of byte array(200)
        self.__wordsDataList = []

        self.functor = None

    def _recv(self):
        raise NotImplementedError()

    def append(self, data):
        if isinstance(data, bytearray):
            if len(data) is 200:
                self._wordsData.append(data)
                return
        if isinstance(data, list):
            for everyData in data:
                self.append(everyData)
            return
        if isinstance(data, tuple):
            for everyData in data:
                self.append(everyData)
            return
        raise ValueError("Undefined data: {0}".format(data))

    def createPacket(self):
        wordsDataLen = len(self._wordsData)
        dataChunkTimeMs = 1.65 * wordsDataLen
        if dataChunkTimeMs > self.periodMS:
            raise ValueError("Critical error: Total Data chunk time if bigger than period!\n"
                             "Words count: {0}. Total time: {1} ms. Period: {2} ms."
                             .format(wordsDataLen, dataChunkTimeMs, self.periodMS))
        for wordData in self._wordsData:
            w = Word708()
            w.data = (c_ubyte * 200)(*wordData)
            w.time = 0
            self.__wordsDataList.append(w)

    def send(self, timeoutMs: int):
        # Initialize SCC TCP Mediator
        if Proxy.STMStartupLocal() is not 1:
            raise LibError("Initialization failed.")

        if Proxy.IsOnline() is 0:
            sleep(0.5)

        if Proxy.IsOnline() is 0:
            raise LibError("Connection failed.")

        self._checkDeviceState()
        # No need to setup 708 channel
        self.createPacket()

        # Initialize raw data array
        wordsRawFirst = (Word708 * len(self.__wordsDataList))(*self.__wordsDataList)

        # Create timeout to raise stop event
        if timeoutMs is not None:
            self._timeoutSend = Process(target=self._stopSendingEx, args=(timeoutMs,))
            self._timeoutSend.start()

        periodMicroseconds = 2000 * self.periodMS
        currentCycle = 1
        self._stopSendingEvent.clear()
        while not self._stopSendingEvent.is_set():
            if self.cycles is not None:
                if currentCycle > self.cycles:
                    break
            outputBufferMicroseconds = Proxy.Get708OutputBufferMicroseconds(self.serialNumber, self.channelNumber)
            if outputBufferMicroseconds < 0:
                raise LibError("outputBufferMicroseconds failed.")
            if periodMicroseconds > outputBufferMicroseconds >= 0:
                sendRec = Proxy.Send708WordsRaw(self.serialNumber, self.channelNumber, byref(wordsRawFirst),
                                                len(self._wordsData))
                if sendRec < 0:
                    raise LibError("Send708WordsRaw failed.")
                self.__wordsDataList[:] = map(self.functor, self.__wordsDataList)
                wordsRawFirst = (Word708 * len(self.__wordsDataList))(*self.__wordsDataList)
                if currentCycle is 1:
                    self.__wordsDataList[0].time = self.periodMS * 100 - (len(self.__wordsDataList) - 1) * 166
                    wordsRawFirst = (Word708 * len(self.__wordsDataList))(*self.__wordsDataList)
                # trace
                # print("Cycle: %d, sent %d Words708." % (currentCycle, sendRec if sendRec >= 0 else 0))
                currentCycle += 1
            sleep(0.02)
        Proxy.ResetOut708Channel(self.serialNumber, self.channelNumber)
        Proxy.Disconnect()
        self._stopSendingEvent.clear()
