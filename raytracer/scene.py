from config import *
import sphere
import camera
import plane
import light
import triangle
from objparser import *

class Scene:
    """
        Holds pointers to all objects in the scene
    """


    def __init__(self):
        """
            Set up scene objects.
        """
        color = [[0.66,0.0,0],[0.33,0.66,0.33],[0.33,0.33,0.66]]

        self.spheres = [
            sphere.Sphere(
                center = [
                    np.random.uniform(low = -1.0, high = 1.0),
                    np.random.uniform(low = -2.0, high = 2.0),
                    np.random.uniform(low = -1.0, high = 1.0)
                ],
                radius = np.random.uniform(low = 0.3, high = 0.3),
                color = [
                    np.random.uniform(low = 0.3, high = 1.0),
                    np.random.uniform(low = 0.3, high = 1.0),
                    np.random.uniform(low = 0.3, high = 1.0)
                ],
                roughness=0.0,
                reflectivity=0.8
                #reflectivity = np.random.uniform(low = 0.3, high = 1.0)
            ) for i in range(8)
        ]
        
        # for _sphere in self.spheres:
        #     print(_sphere.center,_sphere.radius,_sphere.color)
        
        self.planes = []
        self.planes.append( # top
            plane.Plane(
                normal = [0, 0, 1],
                tangent = [0, 1, 0],
                bitangent = [1, 0, 0],
                uMin = -4,
                uMax = 4,
                vMin = -2,
                vMax = 2,
                center = [0, 0, -1],
                material_index = 1
            )
        )
        self.planes.append( # left
            plane.Plane(
                normal = [0, 1, 0],
                tangent = [0, 0, 1],
                bitangent = [1, 0, 0],
                uMin = -2,
                uMax = 2,
                vMin = -2,
                vMax = 2,
                center = [0, 4, 1],
                material_index = 0
            )
        )
        self.planes.append( # right
            plane.Plane(
                normal = [0, -1, 0],
                tangent = [0, 0, 1],
                bitangent = [1, 0, 0],
                uMin = -2,
                uMax = 2,
                vMin = -2,
                vMax = 2,
                center = [0, -4, 1],
                material_index = 3
            )
        )
        self.planes.append( # bottom
            plane.Plane(
                normal = [0, 0, -1],
                tangent = [0, 1, 0],
                bitangent = [1, 0, 0],
                uMin = -4,
                uMax = 4,
                vMin = -2,
                vMax = 2,
                center = [0, 0, 3],
                material_index = 1
            )
        )
        self.planes.append( # fundo
            plane.Plane(
                normal = [-1, 0, 0],
                tangent = [0, 1, 0],
                bitangent = [0, 0, 1],
                uMin = -4,
                uMax = 4,
                vMin = -2,
                vMax = 2,
                center = [2, 0, 1],
                material_index = 1
            )
        )
        
        self.planes.append( # tr'as
            plane.Plane(
                normal = [1, 0, 0],
                tangent = [0, 1, 0],
                bitangent = [0, 0, 1],
                uMin = -8,
                uMax = 8,
                vMin = -8,
                vMax = 8,
                center = [-8, 0, 1],
                material_index = 2
            )
        )         
        
        self.lights = []

        self.lights.append(
            light.Light(
                position = (0,0,0),
                #""" [
                #    np.random.uniform(low = -10, high = 10.0),
                #    np.random.uniform(low = -10.0, high = 10.0),
                #    np.random.uniform(low = -10.0, high = 10.0)
                #] """,
                strength = 3,#np.random.uniform(low = 1.0, high = 200.0),
                color = [
                    np.random.uniform(low = 0.2, high = 1.0),
                    np.random.uniform(low = 0.2, high = 1.0),
                    np.random.uniform(low = 0.2, high = 1.0)
                ],
                radius = 0.25,
                point_count  = 16
            )
        )
        

        objects = ObjParser("models/cube.obj")
        
        self.triangles = []

        model_ratio = 0.4
        
        temp = []
        #objects vem do parser
        self.triangle_temp  = []
        for _object in objects:
            # _object [0] = nome do objeto ||  _object[1] = info dos triangulos
            corners= []
            if(True):
                print("Loading object: "+ _object[0])
                for value in _object[1]:
                    temp.append(value)
                    if len(temp) == 5:
                        corners.append([temp[2]*model_ratio,temp[3]*model_ratio,temp[4]*model_ratio])
                        temp = []
                    if len(corners) == 3:
                        self.triangle_temp.append(corners)
                        corners= []

        positions = [[1,0,0],[0,1,0],[0,0,1]]
        for i,position in enumerate(positions):
            for triangle_corners in self.triangle_temp:
                triangle_t =[]
                for corner in triangle_corners:
                    triangle_t.append([corner[0]+position[0],corner[1]+position[1],corner[2]+position[2]])
                self.triangles.append(triangle.Triangle(corners = triangle_t , color = color[i]))

        

        self.objectCounts = np.array([len(self.spheres), len(self.planes), len(self.lights), len(self.triangles)], dtype = np.int32)
        print(self.objectCounts)
        self.camera = camera.Camera(
            position = [-5, 0, 1]
        )

        self.outDated = True

    def move_player(self, forward,side):

        dPos = forward * self.camera.forwards + side * self.camera.right

        self.camera.position[0] += dPos[0]
        self.camera.position[1] += dPos[1]

    def spin_player(self, dAngle):

        self.camera.theta += dAngle[0]

        if(self.camera.theta < 0):
            self.camera.theta += 360
        if(self.camera.theta > 360):
            self.camera.theta -= 360

        self.camera.phi += dAngle[1]

        if(self.camera.theta < (-1000*360)):
            self.camera.theta = 0
        elif(self.camera.theta > (1000*360)):
            self.camera.theta = 0

        self.camera.recalculateVectors()