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
        self.sphere_count = 8

        # self.spheres = [
        #     sphere.Sphere(
        #         center = [
        #             np.random.uniform(low = -5.0, high = 5.0),
        #             np.random.uniform(low = -5.0, high = 5.0),
        #             np.random.uniform(low = -5.0, high = 5.0)
        #         ],
        #         radius = np.random.uniform(low = 0.3, high = 1.0),
        #         color = [
        #             np.random.uniform(low = 0.3, high = 1.0),
        #             np.random.uniform(low = 0.3, high = 1.0),
        #             np.random.uniform(low = 0.3, high = 1.0)
        #         ],
        #         roughness = np.random.uniform(low = 0.1, high = 1.0),
        #         reflectivity = np.random.uniform(low = 0.3, high = 1.0)
        #     ) for i in range(self.sphere_count)
        # ]

        self.spheres = []
        self.spheres.append(sphere.Sphere(
            center = [1,0,0],
            radius = 0.25,
            color = [
                np.random.uniform(low = 0.3, high = 1.0),
                np.random.uniform(low = 0.3, high = 1.0),
                np.random.uniform(low = 0.3, high = 1.0)
            ], 
            roughness = np.random.uniform(low = 0.0, high = 1.0),
            reflectivity  = np.random.uniform(low = 0.0, high = 1.0)
        ))

        self.spheres.append(sphere.Sphere(
            center = [0,1,0],
            radius = 0.25,
            color = [
                np.random.uniform(low = 0.3, high = 1.0),
                np.random.uniform(low = 0.3, high = 1.0),
                np.random.uniform(low = 0.3, high = 1.0)
            ], 
            roughness = np.random.uniform(low = 0.0, high = 1.0),
            reflectivity  = np.random.uniform(low = 0.0, high = 1.0)
        ))

        self.spheres.append(sphere.Sphere(
            center = [0,0,1],
            radius = 0.25,
            color = [
                np.random.uniform(low = 0.3, high = 1.0),
                np.random.uniform(low = 0.3, high = 1.0),
                np.random.uniform(low = 0.3, high = 1.0)
            ], 
            roughness = np.random.uniform(low = 0.0, high = 1.0),
            reflectivity  = np.random.uniform(low = 0.0, high = 1.0)
        ))

        self.spheres.append(sphere.Sphere(
            center = [1,0,1],
            radius = 0.25,
            color = [
                np.random.uniform(low = 0.3, high = 1.0),
                np.random.uniform(low = 0.3, high = 1.0),
                np.random.uniform(low = 0.3, high = 1.0)
            ], 
            roughness = np.random.uniform(low = 0.0, high = 1.0),
            reflectivity  = np.random.uniform(low = 0.0, high = 1.0)
        ))


        
        # self.planes = [
        #     plane.Plane(
        #         normal = [0, 0, 1],
        #         tangent = [1, 0, 0],
        #         bitangent = [0, 1, 0],
        #         uMin = -0.5,
        #         uMax = 0.5,
        #         vMin = -0.5,
        #         vMax = 0.5,
        #         center = [i%3, i // 3, -1],
        #         material_index = i
        #     ) for i in range(6)
        # ]

        # self.planes.append(plane.Plane(
        #         normal = [0, 0, 1],
        #         tangent = [1, 0, 0],
        #         bitangent = [0, 1, 0],
        #         uMin = -2,
        #         uMax = 2,
        #         vMin = -2,
        #         vMax = 2,
        #         center = [
        #             0,
        #             0,
        #             -4],#center = [i%3, i // 3, -1],
        #         material_index = float(3)
        #     ))
        
        # self.planes.append(plane.Plane(
        #         normal = [0, 0, 1],
        #         tangent = [1, 0, 0],
        #         bitangent = [0, 1, 0],
        #         uMin = -2,
        #         uMax = 2,
        #         vMin = -2,
        #         vMax = 2,
        #         center = [
        #             0,
        #             0,
        #             4],#center = [i%3, i // 3, -1],
        #         material_index = float(2)
        #     ))

        self.planes = []

        self.box_center = self.box_create([0,0,0], [0,1,2,3,2,5])

        for i in range(len(self.box_center)):
            self.planes.append(self.box_center[i])

        # self.box_left = self.box_create([0,0,0], [2,2,2,2,2,2])

        # for i in range(len(self.box_left)):
        #     self.planes.append(self.box_left[i])

        # self.box_right = self.box_create([0,0,0], [2,2,2,2,2,2])

        # for i in range(len(self.box_right)):
        #     self.planes.append(self.box_right[i])


        self.lights = []
        ''' self.lights = [
            light.Light(
                position = (0,0,0),
                #""" [
                #    np.random.uniform(low = -10, high = 10.0),
                #    np.random.uniform(low = -10.0, high = 10.0),
                #    np.random.uniform(low = -10.0, high = 10.0)
                #] """,
                strength = 1,#np.random.uniform(low = 1.0, high = 200.0),
                color = [
                    np.random.uniform(low = 0.2, high = 1.0),
                    np.random.uniform(low = 0.2, high = 1.0),
                    np.random.uniform(low = 0.2, high = 1.0)
                ],
                radius = 1.0,
                point_count  = 16
            ) for i in range(1)
        ] '''

        self.lights.append(light.Light(
            position = (0,0,-1),
            strength=1,
            color = (1.0,1.0,1.0),
            radius=0.05,
            point_count = 16
        ))

        # self.lights.append(light.Light(
        #     position = (-5,0,0),
        #     strength=5,
        #     color = (np.random.uniform(low = 0.2, high = 1.0),np.random.uniform(low = 0.2, high = 1.0),np.random.uniform(low = 0.2, high = 1.0)),
        #     radius=0.25,
        #     point_count = 16
        # ))
        
        self.camera = camera.Camera(
            position = [-1, 0, 0]
        )

        self.objectCounts = np.array([len(self.spheres), len(self.planes), len(self.lights)], dtype = np.int32)

        self.outDated = True

    def box_create(self, center, index):
        planes = []
        # planes.append( # top
        #     plane.Plane(
        #         normal = [0, 0, 1],
        #         tangent = [0, 1, 0],
        #         bitangent = [1, 0, 0],
        #         uMin = -4,
        #         uMax = 4,
        #         vMin = -2,
        #         vMax = 2,
        #         center = [0 + center[0], 0 + center[1], -1 + center[2]],
        #         material_index = index[0]
        #     )
        # )
        planes.append( # left
            plane.Plane(
                normal = [0, 1, 0],
                tangent = [0, 0, 1],
                bitangent = [1, 0, 0],
                uMin = -2,
                uMax = 2,
                vMin = -2,
                vMax = 2,
                center = [0+ center[0], 4+ center[1], 1 + center[2]],
                material_index = index[1]
            )
        )
        planes.append( # right
            plane.Plane(
                normal = [0, -1, 0],
                tangent = [0, 0, 1],
                bitangent = [1, 0, 0],
                uMin = -2,
                uMax = 2,
                vMin = -2,
                vMax = 2,
                center = [0+ center[0], -4+ center[1], 1+ center[2]],
                material_index = index[2]
            )
        )
        planes.append( # bottom
            plane.Plane(
                normal = [0, 0, -1],
                tangent = [0, 1, 0],
                bitangent = [1, 0, 0],
                uMin = -4,
                uMax = 4,
                vMin = -2,
                vMax = 2,
                center = [0+ center[0], 0+ center[1], 3+ center[2]],
                material_index = index[3]
            )
        )
        planes.append( # fundo
            plane.Plane(
                normal = [-1, 0, 0],
                tangent = [0, 1, 0],
                bitangent = [0, 0, 1],
                uMin = -4,
                uMax = 4,
                vMin = -2,
                vMax = 2,
                center = [2+ center[0], 0+ center[1], 1+ center[2]],
                material_index = index[4]
            )
        )
        
        # planes.append( # tr'as
        #     plane.Plane(
        #         normal = [1, 0, 0],
        #         tangent = [0, 1, 0],
        #         bitangent = [0, 0, 1],
        #         uMin = -8,
        #         uMax = 8,
        #         vMin = -8,
        #         vMax = 8,
        #         center = [-8+ center[0], 0+ center[1], 1+ center[2]],
        #         material_index = index[5]
        #     )
        # )

        return planes

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