class Rectangle:
    __slots__ = ["pt1", "pt2"]
    def __init__(self, pt1, pt2):
        self.pt1 = pt1
        self.pt2 = pt2
    def getArea(self):
        return int((self.pt2.x - self.pt1.x) * (self.pt2.y - self.pt1.y))