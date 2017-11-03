import os
import xml.etree.ElementTree as ET


"""
    #Example:

    path_to_xml = os.path.abspath(os.path.join(os.path.dirname(__file__), '../path/file.xml'))
    waypoints = import_waypoints_from_xml(path_to_xml)

    if waypoints is not None:
        for wp in waypoints:
            print("Waypoint: ")
            print(wp.__dict__)
"""


class Waypoint:
    def __init__(self):
        # 0
        self.Index: int = 0
        #
        self.Name: str = ""
        # 0
        self.Longitude = 0.0
        # 0
        self.Latitude = 0.0
        # "WayPoint"
        self.PPMType: str = "WayPoint"
        # "WP"
        self.STType: str = "WP"
        # True
        self.IsOnRoute: bool = True
        # False
        self.IsArcExist: bool = False
        # 0
        self.ArcInboundCourse = 0.0
        # 0
        self.ArcRadius = 0.0
        # 0
        self.ArcCourseChange = 0.0
        # False
        self.IsGap: bool = False


def import_waypoints_from_xml(path):
    if os.path.isfile(path) is False:
        return None

    tree = ET.parse(path)
    root = tree.getroot()

    waypoints = []

    for waypoint in root.findall('WayPoint'):
        temp_wp = Waypoint()
        # print("WayPoint")
        elemList = []
        for elem in waypoint:
            elemList.append(elem.tag)
        for elem in elemList:
            field = waypoint.find(elem)
            if len(field) is not 0:
                # print("\t", str(elem).ljust(max(len(str(ddd)) for ddd in elemList)), field[0].text)
                if field[0].text is not None:
                    setattr(temp_wp, elem, field[0].text)
                continue
            text = field.text
            # print("\t", str(elem).ljust(max(len(str(ddd)) for ddd in elemList)), text)
            if text is not None:
                setattr(temp_wp, elem, text)
        waypoints.append(temp_wp)

    return waypoints
