class Point:
    def __init__(self, x, y):
        self.x = x
        self.y = y


def change(point=Point):
    newlist = [point]
    newlist[0].x = 10


point1 = Point(1, 2)
point2 = Point(3, 4)

list = [point1, point2]
list[0].x = 5

print(point1.x, point1.y, point2.x, point2.y)
print(point1.x)

change(point1)

print(list[0].x, point1.y, point2.x, point2.y)
print(point1.x)
