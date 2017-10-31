# import unittest
# import Scenarios
# from ArincTypes import Rates, Arinc429ParityTypeOut
# from MediatorClientWrapper import STMStartupLocal, IsOnline
# from time import sleep
#
# initRes = STMStartupLocal()
#
#
# class TestAssistant:
#     @staticmethod
#     def create429DataListOfTypes(count, dataType):
#         return [dataType(x) for x in range(count)]
#
#     @staticmethod
#     def create429DataListOfNestedList(count):
#         resList = []
#         index = 0
#         while index < count:
#             resList.append(index)
#             index = index + 1
#         return resList
#
#     @staticmethod
#     def isServiceOnline(timeout_ms):
#         if timeout_ms > 0:
#             if IsOnline() is 1:
#                 return True
#             else:
#                 sleep(0.2)
#                 return TestAssistant.isServiceOnline(timeout_ms - 200)
#         return False
#
#
# class TestScenariosAddRemoveData(unittest.TestCase):
#     def test_add_429_word_data_by_list_of_int(self):
#         wordCount = 6
#         data6Elements = TestAssistant.create429DataListOfTypes(wordCount, int)
#         testS = Scenarios.Settings429(None, 1, Rates.R100, Arinc429ParityTypeOut.NoChange, 200)
#         testS.append(data6Elements)
#         wordInSc = testS.count()
#         self.assertTrue(wordCount == wordInSc)
#
#     def test_add_429_word_data_by_list_of_mixed_types_of_ints(self):
#         wordCount = 8
#         data6Elements = [1, [2, 3, 4], 5, [6, 7, 8]]
#         testS = Scenarios.Settings429(None, 1, Rates.R100, Arinc429ParityTypeOut.NoChange, 200)
#         testS.append(data6Elements)
#         wordInSc = testS.count()
#         self.assertTrue((wordCount == wordInSc))
#
#     def test_add_429_word_data_by_single_int(self):
#         wordCount = 1
#         testS = Scenarios.Settings429(None, 1, Rates.R100, Arinc429ParityTypeOut.NoChange, 200)
#         testS.append(wordCount)
#         wordInSc = testS.count()
#         self.assertTrue((wordCount == wordInSc))
#
#     def test_remove_1_element(self):
#         testS = Scenarios.Settings429(None, 1, Rates.R100, Arinc429ParityTypeOut.NoChange, 200)
#         wordCount = 10
#         data6Elements = TestAssistant.create429DataListOfTypes(wordCount, int)
#         testS.append(data6Elements)
#         deletedCount = testS.remove(1)
#         self.assertTrue(deletedCount is 1)
#         self.assertTrue((wordCount-1) is testS.count())
#
#     def test_remove_by_range(self):
#         testS = Scenarios.Settings429(None, 1, Rates.R100, Arinc429ParityTypeOut.NoChange, 200)
#         wordCount = 16
#         startIndex = 1
#         endIndex = 6
#         data6Elements = TestAssistant.create429DataListOfTypes(wordCount, int)
#         testS.append(data6Elements)
#         deletedCount = testS.remove(startIndex, endIndex)
#         dif = endIndex - startIndex
#         self.assertTrue(dif == deletedCount)
#
#
# @unittest.skipIf(TestAssistant.isServiceOnline(1000) is False, "not supported in this library version")
# class TestScenariosAuxiliary(unittest.TestCase):
#     def test_device_checker(self):
#         testS = Scenarios.Settings429(None, 1, Rates.R100, Arinc429ParityTypeOut.NoChange, 200)
#         try:
#             testS._checkDeviceState()
#         except Scenarios.DeviceError as error:
#             testMessage = error.message if hasattr(error, "message") else "Error"
#             self.fail(testMessage)
#         except Scenarios.LibError as error:
#             testMessage = error.message if hasattr(error, "message") else "Error"
#             self.fail(testMessage)
#
# # class TestScenariosSend(unittest.TestCase):
# #     pass
# #
# #
# # class TestScenariosReceive(unittest.TestCase):
# #     pass
#
#
# if __name__ == '__main__':
#     unittest.main()
#
