from Arinc_IO.TrackParser import TrackInfo
import os

tr = TrackInfo()
path_to_bin = os.path.abspath(os.path.join(os.path.dirname(__file__), '../bin trace//маршрут3_процедура.scc429'))
tr.import_track(path_to_bin)
