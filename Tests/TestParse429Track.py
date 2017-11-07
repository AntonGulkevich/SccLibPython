from Arinc_IO.TrackParser import TrackInfo
import os

# 429
"""
маршрут3_процедура.scc429
"""
# 708
"""
1_Arinc708.sccr
2_Arinc708.sccr
"""
tr = TrackInfo()
path_to_bin = os.path.abspath(os.path.join(os.path.dirname(__file__), '../bin trace//1_Arinc708.sccr'))
tr.import_track(path_to_bin)
