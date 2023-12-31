from config import * 
import sphere
import camera
import plane

class Scene:


    def __init__(self):


        self.spheres = [
            sphere.Sphere(
                center = [
                    np.random.uniform(low= 3.0, high = 10.0),
                    np.random.uniform(low= -5.0, high = 5.0),
                    np.random.uniform(low=-5.0, high = 5.0)
                ],
                radius = np.random.uniform(low = 0.1 , high = 2.0),
                color = [
                    np.random.uniform(low= 0.3, high = 1.0),
                    np.random.uniform(low= 0.3, high = 1.0),
                    np.random.uniform(low= 0.3, high = 1.0)
                ]
            ) for i in range(32)
        ]

        self.camera = camera.Camera(
            position = [-5,0,0]
        )

        self.plane = [
            plane.Plane(
                normal = [0,0,1],
                tangent = [1,0,0],
                bitangent = [0,1,0],
                uMin = -10,
                uMax = -10,
                vMin = -10,
                vMax = 10,
                center = [0,0,-7],
                color = [
                    np.random.uniform(low= 0.3, high = 1.0),
                    np.random.uniform(low= 0.3, high = 1.0),
                    np.random.uniform(low= 0.3, high = 1.0)
                ]
            ),
        ]

        self.outDated = True