from config import *

class Light:
    
    
    def __init__(self, position, color, strength,radius, point_count):
        self.position = np.array(position, dtype = np.float32)
        self.color = np.array(color, dtype = np.float32)
        self.strength = strength
        self.radius = radius
        