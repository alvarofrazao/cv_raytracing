from config import *
import buffer
import material
import scene
import screen_quad
import megatexture
import cubemap 

class Engine:
    """
        Responsible for drawing scenes
    """

    def __init__(self, width, height):
        """
            Initialize a flat raytracing context
            
                Parameters:
                    width (int): width of screen
                    height (int): height of screen
        """

        self.screenWidth = width
        self.screenHeight = height


        self.makeAssets()
        self.createNoiseTexture()
    
    def createShader(self, vertexFilepath, fragmentFilepath):
        """
            Read source code, compile and link shaders.
            Returns the compiled and linked program.
        """

        with open(vertexFilepath,'r') as f:
            vertex_src = f.readlines()

        with open(fragmentFilepath,'r') as f:
            fragment_src = f.readlines()
        
        shader = compileProgram(compileShader(vertex_src, GL_VERTEX_SHADER),
                                compileShader(fragment_src, GL_FRAGMENT_SHADER))
        
        return shader
    
    def createMegaTexture(self):

        filenames = [
            "Wood067","MetalPlates", "Metal01","Marble06","Plastic012","Rubber04"
        ]

        self.megaTexture = megatexture.MegaTexture(filenames)

    def createNoiseTexture(self) -> None:

        """
            generate four screens' worth of noise
        """

        self.noiseData = np.zeros(self.screenHeight * self.screenWidth * 16, dtype=np.float32)

        # random noise: (x y z -)
        for i in range(self.screenHeight * self.screenWidth * 4):
            radius = np.random.uniform(low = 0.0, high = 0.99)
            theta = np.random.uniform(low = 0.0, high = 2 * np.pi)
            phi = np.random.uniform(low = 0.0, high = np.pi)
            variation = np.array(
                [
                    radius * np.cos(theta) * np.cos(phi), 
                    radius * np.sin(theta) * np.cos(phi), 
                    radius * np.sin(phi)
                ], dtype=np.float32
            )
            self.noiseData[4*i:4*i+3] = variation[:]

        self.noiseTexture = glGenTextures(1)
        glActiveTexture(GL_TEXTURE2)
        glBindTexture(GL_TEXTURE_2D, self.noiseTexture)

        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)
    
        glTexImage2D(
            GL_TEXTURE_2D,0,GL_RGBA32F, 
            4 * self.screenWidth,self.screenHeight,
            0,GL_RGBA,GL_FLOAT,bytes(self.noiseData)
        )
    
    def createComputeShader(self, filepath):
        """
            Read source code, compile and link shaders.
            Returns the compiled and linked program.
        """

        with open(filepath,'r') as f:
            compute_src = f.readlines()
        
        shader = compileProgram(compileShader(compute_src, GL_COMPUTE_SHADER))
        
        return shader

    def makeAssets(self) -> None:
        """ Make all the stuff. """

        self.screenQuad = screen_quad.ScreenQuad()

        self.colorBuffer = material.Material(self.screenWidth, self.screenHeight)

        self.createMegaTexture()
        

        self.sphereBuffer = buffer.Buffer(size = 1024, binding = 1, floatCount = 12)
        self.planeBuffer = buffer.Buffer(size = 1024, binding = 2, floatCount = 20)
        self.lightBuffer = buffer.Buffer(size = 2, binding = 4, floatCount = 8)

        self.shader = self.createShader("shaders/frameBufferVertex.txt",
                                        "shaders/frameBufferFragment.txt")
        
        self.rayTracerShader = self.createComputeShader("shaders/rayTracer.glsl")

        self.skybox = cubemap.CubeMap("Skybox")

        glUseProgram(self.rayTracerShader)
        glUniform1i(glGetUniformLocation(self.rayTracerShader,"skybox"),6)
    
    def updateScene(self, _scene: scene.Scene) -> None:

        _scene.outDated = False

        glUseProgram(self.rayTracerShader)

        for i,_sphere in enumerate(_scene.spheres):
            self.sphereBuffer.recordSphere(i, _sphere)

        for i,_plane in enumerate(_scene.planes):
            self.planeBuffer.recordPlane(i, _plane)
        
        for i,light in enumerate(_scene.lights):
            self.lightBuffer.recordLight(i,light)


        self.sphereBuffer.readFrom()
        self.planeBuffer.readFrom()
        self.lightBuffer.readFrom()

        glUniform3iv(glGetUniformLocation(self.rayTracerShader, "objectCounts"), 1, _scene.objectCounts)

    def prepareScene(self, _scene: scene.Scene) -> None:
        """
            Send scene data to the shader.
        """

        glUseProgram(self.rayTracerShader)

        glUniform3fv(glGetUniformLocation(self.rayTracerShader, "viewer.position"), 1, _scene.camera.position)
        glUniform3fv(glGetUniformLocation(self.rayTracerShader, "viewer.forwards"), 1, _scene.camera.forwards)
        glUniform3fv(glGetUniformLocation(self.rayTracerShader, "viewer.right"), 1, _scene.camera.right)
        glUniform3fv(glGetUniformLocation(self.rayTracerShader, "viewer.up"), 1, _scene.camera.up)

        self.skybox.use()

        if _scene.outDated:
            self.updateScene(_scene)

        glActiveTexture(GL_TEXTURE6)
        glBindImageTexture(6, self.noiseTexture, 0, GL_FALSE, 0, GL_READ_ONLY, GL_RGBA32F)
        
    def renderScene(self, _scene: scene.Scene) -> None:
        """
            Draw all objects in the scene
        """
        
        glUseProgram(self.rayTracerShader)

        self.prepareScene(_scene)

        self.colorBuffer.writeTo()
        
        glDispatchCompute(int(self.screenWidth/8), int(self.screenHeight/8), 1)
  
        # make sure writing to image has finished before read
        glMemoryBarrier(GL_SHADER_IMAGE_ACCESS_BARRIER_BIT)

        self.drawScreen()

    def drawScreen(self) -> None:
        glUseProgram(self.shader)
        glBindFramebuffer(GL_FRAMEBUFFER, 0)
        self.colorBuffer.readFrom()
        self.screenQuad.draw()
        pg.display.flip()
    
    def destroy(self):
        """
            Free any allocated memory
        """
        glUseProgram(self.rayTracerShader)
        glMemoryBarrier(GL_ALL_BARRIER_BITS)
        glDeleteProgram(self.rayTracerShader)
        self.screenQuad.destroy()
        self.colorBuffer.destroy()
        self.sphereBuffer.destroy()
        self.planeBuffer.destroy()
        self.lightBuffer.destroy()
        glDeleteProgram(self.shader)