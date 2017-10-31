# Namespace for windows types
from ctypes.wintypes import *
import ctypes
import os
from time import sleep

# Handle for dll
mediatorDLL = ctypes.WinDLL(os.path.dirname(os.path.abspath(__file__)) + os.path.sep + "../Lib/SccMediator64.dll")
sccLib = ctypes.WinDLL(os.path.dirname(os.path.abspath(__file__)) + os.path.sep + "../Lib/SccDeviceLib64.dll")


class LibError(Exception):
    def __init__(self, message, error_code=None):

        self.message = "SCC TCP Mediator: " + message
        if error_code is not None:
            self.message = self.message + " Error code: " + str(error_code)
        super().__init__(self.message)


def STMStartupLocal():
    """
    InitializeEnvironment SCC TCP Mediator with default parameters for loopback address
    Return ZERO on success, error code on failure
    """
    initRes = mediatorDLL.STMStartupLocal()
    return initRes


def STMStartup(hostNameTCP, port, hostNameUDP):
    """
    Return ZERO on success, error code on failure
    :param hostNameTCP:
    :param port:
    :param hostNameUDP:
    :return:
    """
    initRes = mediatorDLL.STMStartup(hostNameTCP, port, hostNameUDP)
    return initRes


def IsOnline():
    """
    :return: status of connection: true if connections established with server, false - if no connections
    """
    state = mediatorDLL.IsOnline()
    return state


def Ping():
    """
    :return: time in microseconds needed to process simple command via TCP
    """
    initRes = mediatorDLL.Ping()
    return initRes


def Disconnect():
    """
    Close all UDP/TCP streams connected with this thread
    """
    mediatorDLL.Disconnect()
    return


def GetAvailableChannelsIn(deviceSerialNum):
    """
    Return INT, bits in one mean is channel avaliable or not
    1 - is available, 0 - is aready on use
    first 4 bits bits are 1-4 numbers of 429 channels
    5th bit is 708 channel
    If the function fails, the return value is negative error code
    If the function succeeds, the return value is (0-31)
    """
    availableChannels = mediatorDLL.GetAvalibleChannelsIn(deviceSerialNum)
    return availableChannels


def GetAvailableChannelsOut(deviceSerialNum):
    """
    Return INT, bits in one mean is channel avaliable or not
    1 - is available, 0 - is aready on use
    first 4 bits bits are 1-4 numbers of 429 channels
    5th bit is 708 channel
    If the function fails, the return value is negative error code
    If the function succeeds, the return value is (0-31)
    """
    availableChannels = mediatorDLL.GetAvalibleChannelsOut(deviceSerialNum)
    return availableChannels


def ReleaseChannel429In(deviceSerialNum, channelNum):
    """
    Release channel
    :param deviceSerialNum:
    :param channelNum:
    :return: TRUE on success, error code on failure
    """
    res = mediatorDLL.ReleaseChannel429In(deviceSerialNum, channelNum)
    return res


def ReleaseChannel429Out(deviceSerialNum, channelNum):
    """
    Release channel
    :param deviceSerialNum:
    :param channelNum:
    :return: TRUE on success, error code on failure
    """
    res = mediatorDLL.ReleaseChannel429Out(deviceSerialNum, channelNum)
    return res


def ReleaseChannel708In(deviceSerialNum, channelNum):
    """
    Release channel
    :param deviceSerialNum:
    :param channelNum:
    :return: TRUE on success, error code on failure
    """
    res = mediatorDLL.ReleaseChannel708In(deviceSerialNum, channelNum)
    return res


def ReleaseChannel708Out(deviceSerialNum, channelNum):
    """
    Release channel
    :param deviceSerialNum:
    :param channelNum:
    :return: TRUE on success, error code on failure
    """
    res = mediatorDLL.ReleaseChannel708Out(deviceSerialNum, channelNum)
    return res


def ConnectForced429In(deviceSerialNum, channelNum):
    """
    :param deviceSerialNum:
    :param channelNum:
    :return: TRUE on success, error code on failure
    """
    res = mediatorDLL.ConnectForced429In(deviceSerialNum, channelNum)
    return res


def ConnectForced429Out(deviceSerialNum, channelNum):
    """
    :param deviceSerialNum:
    :param channelNum:
    :return: TRUE on success, error code on failure
    """
    res = mediatorDLL.ConnectForced429Out(deviceSerialNum, channelNum)
    return res


def ConnectForced708In(deviceSerialNum, channelNum):
    """
    :param deviceSerialNum:
    :param channelNum:
    :return: TRUE on success, error code on failure
    """
    res = mediatorDLL.ConnectForced708In(deviceSerialNum, channelNum)
    return res


def ConnectForced708Out(deviceSerialNum, channelNum):
    """
    :param deviceSerialNum:
    :param channelNum:
    :return: TRUE on success, error code on failure
    """
    res = mediatorDLL.ConnectForced708Out(deviceSerialNum, channelNum)
    return res


# region SccLib Functions

# Количество подключенных устройств
def GetDeviceCount():
    """
    If the function fails, the return value is MANAGER_NOT_INITIALIZED.
    If the function succeeds, the return value is nonnegative.
    """
    res = mediatorDLL.GetDeviceCount()
    return res


def Set429InputChannelParams(deviceSerialNum, channelNum, rate, parityType):
    """
    Установить параметры входного канала Arinc429
    :param deviceSerialNum: Серийный номер устройства
    :param channelNum: Номер канала в устройстве (0 - 3)
    :param rate: Скорость
    :param parityType: Четность
    :return: If the function fails, the return value is negative error code.
    If the function succeeds, the return value is zero.
    """
    res = mediatorDLL.Set429InputChannelParams(deviceSerialNum, channelNum, rate, parityType)
    return res


def GetDeviceNumsRaw(max_size):
    """
    Список серийный номеров подключенных устройств
    :param max_size:
    :return:If the function fails, the return value is negative error code.
    If the function succeeds, the return value is non-negative value.
    """
    nums = (UINT * max_size)()

    err = mediatorDLL.GetDeviceNumsRaw(nums, max_size)
    pyArr = []
    if err < 0:
        pyArr.append(pyArr)
        return pyArr
    for i in nums:
        pyArr.append(i)
    return pyArr


def Set429OutputChannelParams(deviceSerialNum, channelNum, rate, parityType):
    """
    Установить параметры выходного канала Arinc429
    :param deviceSerialNum: Серийный номер устройства
    :param channelNum: Номер канала в устройстве (0 - 3)
    :param rate: Скорость
    :param parityType: Четность
    :return: If the function fails, the return value is negative error code.
    If the function succeeds, the return value is zero.
    """
    res = mediatorDLL.Set429OutputChannelParams(deviceSerialNum, channelNum, rate, parityType)
    return res


def Get429OutputBufferWordsCount(deviceSerialNum, channelNum):
    """
    brief Количество неотправленных слов в выходном канале Arinc708
    param deviceSerialNum Серийный номер устройства
    param channelNum Номер канала в устройстве (всегда 0)
    return If the function fails, the return value is negative error code.
    return If the function succeeds, the return value is non-negative value.
    """
    res = mediatorDLL.Get429OutputBufferWordsCount(deviceSerialNum, channelNum)
    return res


def Get708OutputBufferWordsCount(deviceSerialNum, channelNum):
    """
    brief Количество неотправленных слов в выходном канале Arinc708
    param deviceSerialNum Серийный номер устройства
    param channelNum Номер канала в устройстве (всегда 0)
    return If the function fails, the return value is negative error code.
    return If the function succeeds, the return value is non-negative value.
    """
    res = mediatorDLL.Get708OutputBufferWordsCount(deviceSerialNum, channelNum)
    return res


def Get429OutputBufferMicroseconds(deviceSerialNum, channelNum):
    """
    brief Суммарное время неотправленных слов в выходном канале Arinc429 в мкс
    param deviceSerialNum Серийный номер устройства
    param channelNum Номер канала в устройстве (0 - 3)
    return If the function fails, the return value is negative error code.
    return If the function succeeds, the return value is non-negative value.
    """
    res = mediatorDLL.Get429OutputBufferMicroseconds(deviceSerialNum, channelNum)
    return res


def Get708OutputBufferMicroseconds(deviceSerialNum, channelNum):
    """
    brief Суммарное время неотправленных слов в выходном канале Arinc708 в мкс
    param deviceSerialNum Серийный номер устройства
    param channelNum Номер канала в устройстве (всегда 0)
    return If the function fails, the return value is negative error code.
    return If the function succeeds, the return value is non-negative value.
    """
    res = mediatorDLL.Get708OutputBufferMicroseconds(deviceSerialNum, channelNum)
    return res


def Set429InputBufferLength(deviceSerialNum, channelNum, wordsCount):
    """
    brief Установить максимальное количество слов во входном буфере канала Arinc429 (старые слова будут удаляться)
    param deviceSerialNum Серийный номер устройства
    param channelNum Номер канала в устройстве (0 - 3)
    param wordsCount количество слов в штуках (Word429)
    return If the function fails, the return value is negative error code.
    return If the function succeeds, the return value is zero.
    """
    res = mediatorDLL.Set429InputBufferLength(deviceSerialNum, channelNum, wordsCount)
    return res


def Set708InputBufferLength(deviceSerialNum, channelNum, wordsCount):
    """
    brief Установить максимальное количество слов во входном буфере канала Arinc708 (старые слова будут удаляться)
    param deviceSerialNum Серийный номер устройства
    param channelNum Номер канала в устройстве (всегда 0)
    param wordsCount количество слов в штуках (Word708)
    return If the function fails, the return value is negative error code.
    return If the function succeeds, the return value is zero.
    """
    res = mediatorDLL.Set708InputBufferLength(deviceSerialNum, channelNum, wordsCount)
    return res


def ResetOut429Channel(deviceSerialNum, channelNum):
    """
    brief Очистка выходного буфера канала Arinc429
    param deviceSerialNum Серийный номер устройства
    param channelNum Номер канала в устройстве (0 - 3)
    return If the function fails, the return value is negative error code.
    return If the function succeeds, the return value is zero.
    """
    res = mediatorDLL.ResetOut429Channel(deviceSerialNum, channelNum)
    return res


def ResetOut708Channel(deviceSerialNum, channelNum):
    """
    brief Очистка выходного буфера канала Arinc708
    param deviceSerialNum Серийный номер устройства
    param channelNum Номер канала в устройстве (всегда 0)
    return If the function fails, the return value is negative error code.
    return If the function succeeds, the return value is zero.
    """
    res = mediatorDLL.ResetOut708Channel(deviceSerialNum, channelNum)
    return res


def ResetIn429Channel(deviceSerialNum, channelNum):
    """
    brief Очистка входного буфера канала Arinc429
    param deviceSerialNum Серийный номер устройства
    param channelNum Номер канала в устройстве (0 - 3)
    return If the function fails, the return value is negative error code.
    return If the function succeeds, the return value is zero.
    """
    res = mediatorDLL.ResetIn429Channel(deviceSerialNum, channelNum)
    return res


def ResetIn708Channel(deviceSerialNum, channelNum):
    """
    brief Очистка входного буфера канала Arinc708
    param deviceSerialNum Серийный номер устройства
    param channelNum Номер канала в устройстве (всегда 0)
    return If the function fails, the return value is negative error code.
    return If the function succeeds, the return value is zero.
    """
    res = mediatorDLL.ResetIn708Channel(deviceSerialNum, channelNum)
    return res


def SetDeviceAttachedHandler(handler):
    """
    Устанавливает функцию для обработки события при появлении нового устройства
    :param handler:
    :return:
    """
    mediatorDLL.SetDeviceAttachedHandler(handler)
    return


def SetDeviceDetachedHandler(handler):
    """
    Устанавливает функцию для обработки события при пропадании устройства
    :param handler:
    :return:
    """
    mediatorDLL.SetDeviceDetachedHandler(handler)
    return


def Send429WordsRaw(deviceSerialNum, channelNum, words, count):
    """
    brief Отправить список слов Arinc429 в формате структуры Word429 (время, данные)
    param deviceSerialNum Серийный номер устройства
    param channelNum Номер канала в устройстве (0 - 3)
    param words Список слов
    return If the function fails, the return value is negative error code.
    return If the function succeeds, the return value is non-negative value.
    """
    res = mediatorDLL.Send429WordsRaw(deviceSerialNum, channelNum, words, count)
    return res


def Receive429WordsRaw(deviceSerialNum, channelNum, words, count):
    """
    brief Получить список принятых слов Arinc429 в формате структуры Word429 (время, данные)
    param deviceSerialNum Серийный номер устройства
    param channelNum Номер канала в устройстве (0 - 3)
    param words Список слов
    return If the function fails, the return value is negative error code.
    return If the function succeeds, the return value is non-negative value.
    """
    res = mediatorDLL.Receive429WordsRaw(deviceSerialNum, channelNum, words, count)
    return res


def Send708WordsRaw(deviceSerialNum, channelNum, words, count):
    """
    brief Отправить список слов Arinc708 в формате структуры Word708 (время, данные(200 байт))
    param deviceSerialNum Серийный номер устройства
    param channelNum Номер канала в устройстве (всегда 0)
    param words Список слов
    return If the function fails, the return value is negative error code.
    return If the function succeeds, the return value isnon-negative value.
    """
    res = mediatorDLL.Send708WordsRaw(deviceSerialNum, channelNum, words, count)
    return res


def Receive708WordsRaw(deviceSerialNum, channelNum, words, count):
    """
    brief Получить список принятых слов Arinc708 в формате структуры Word708 (время, данные(200 байт))
    param deviceSerialNum Серийный номер устройства
    param channelNum Номер канала в устройстве (всегда 0)
    param words Список слов
    return If the function fails, the return value is negative error code.
    return If the function succeeds, the return value is non-negative value.
    """
    res = mediatorDLL.Receive708WordsRaw(deviceSerialNum, channelNum, words, count)
    return res


def GetPinConfiguration(deviceSerialNum):
    """
    brief Получить конфигурацию разъема
    return If the function fails, the return value is negative error code.
    return If the function succeeds, the return value is pin configuration value value.
    """
    res = mediatorDLL.GetPinConfiguration(deviceSerialNum)
    return res


def GetDllVersion():
    """
    brief Получить версию библиотеки ППК
    return If the function fails, the return value is negative error code.
    return If the function succeeds, the return value is dll version positive value.
    """
    res = mediatorDLL.GetDllVersion()
    return res
# endregion
