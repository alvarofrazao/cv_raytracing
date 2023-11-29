from config import *
import sphere
import camera
import plane

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
                    np.random.uniform(low = -5.0, high = 5.0),
                    np.random.uniform(low = -5.0, high = 5.0)
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
                material_index = 1
            ) for i in range(9)
        ]
        
        self.camera = camera.Camera(
            position = [-1, 0, 0]
        )

        self.objectCounts = np.array([len(self.spheres), len(self.planes)], dtype = np.int32)

        self.outDated = True