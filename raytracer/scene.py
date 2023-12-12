from config import *
import sphere
import camera
import plane
import light

class Scene:
    """
        Holds pointers to all objects in the scene
    """


    def __init__(self):
        """
            Set up scene objects.
        """
        
        self.spheres = [
            sphere.Sphere(
                center = [
                    np.random.uniform(low = 3.0, high = 10.0),
                    np.random.uniform(low = -5.0, high = 10.0),
                    np.random.uniform(low = -5.0, high = 10.0)
                ],
                radius = np.random.uniform(low = 0.3, high = 2.0),
                color = [
                    np.random.uniform(low = 0.3, high = 1.0),
                    np.random.uniform(low = 0.3, high = 1.0),
                    np.random.uniform(low = 0.3, high = 1.0)
                ]
            ) for i in range(16)
        ]
        
        self.planes = [
            plane.Plane(
                normal = [0, 0, 1],
                tangent = [1, 0, 0],
                bitangent = [0, 1, 0],
                uMin = -0.5,
                uMax = 0.5,
                vMin = -0.5,
                vMax = 0.5,
                center = [i%3, i // 3, -1],
                material_index = i
            ) for i in range(6)
        ]

        self.planes.append(plane.Plane(
                normal = [0, 0, 1],
                tangent = [1, 0, 0],
                bitangent = [0, 1, 0],
                uMin = -2,
                uMax = 2,
                vMin = -2,
                vMax = 2,
                center = [
                    0,
                    0,
                    -4],#center = [i%3, i // 3, -1],
                material_index = float(3)
            ))
        
        self.planes.append(plane.Plane(
                normal = [0, 0, 1],
                tangent = [1, 0, 0],
                bitangent = [0, 1, 0],
                uMin = -2,
                uMax = 2,
                vMin = -2,
                vMax = 2,
                center = [
                    0,
                    0,
                    4],#center = [i%3, i // 3, -1],
                material_index = float(2)
            ))

        self.lights = [
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
            ) for i in range(1)
        ]

        self.lights.append(light.Light(
            position = (0,0,4),
            strength=50,
            color = (np.random.uniform(low = 0.2, high = 1.0),np.random.uniform(low = 0.2, high = 1.0),np.random.uniform(low = 0.2, high = 1.0)),
            radius=0.25,
            point_count = 16
        ))

        self.lights.append(light.Light(
            position = (0,0,0),
            strength=100,
            color = (np.random.uniform(low = 0.2, high = 1.0),np.random.uniform(low = 0.2, high = 1.0),np.random.uniform(low = 0.2, high = 1.0)),
            radius=0.25,
            point_count = 16
        ))
        
        self.camera = camera.Camera(
            position = [-1, 0, 0]
        )

        self.objectCounts = np.array([len(self.spheres), len(self.planes), len(self.lights)], dtype = np.int32)

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