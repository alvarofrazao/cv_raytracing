from config import * 


class Sphere:

    def __init__(self,center,radius,color):
        self.type = 1
        self.center = np.array(center,dtype = np.float32)
        self.radius = radius
        self.color = np.array(color,dtype = np.float32)
        self.roughness = 0.0
        self.reflectivity = 1.0