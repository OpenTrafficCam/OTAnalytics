from shapely.geometry import Polygon, LineString, Point
import geopandas as gpd

point_ding = Point((0,10))
polygon = Polygon([(0, 0), (1, 0), (1, 1), (0, 1), (0, 0)])
line1 = LineString([(0.5, 0.5), (0.7, 0.7), (0.1, 0.1), (0.197, 0.1687)])
line2 = LineString([(0.9, 0.9), (0.2, 0.6)])


# if isinstance(polygon, Polygon):
#     print("its polygon")

# else:
#     print("did not work")

for point in line1.boundary:
    print(point)






