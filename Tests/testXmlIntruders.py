from Arinc_IO.xml import Intruder, import_intruders_from_xml
import os


"""
FDVO_border_32_1
"""
path_to_xml = os.path.abspath(os.path.join(os.path.dirname(__file__), '../bin trace//FDVO_border_32_1'))
intruders = import_intruders_from_xml(path_to_xml)

print("{}".format([intr.__dict__ for intr in intruders]))