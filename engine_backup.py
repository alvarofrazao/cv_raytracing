from config import *
import screen_quad
import material

class Engine:
    """
        Responsible for drawing scenes
    """

    def __init__(self, width: int, height: int):
        """
            Initialize a flat raytracing context
            
                Parameters:
                    width (int): width of screen
                    height (int): height of screen
        """
        self.screenWidth = width
        self.screenHeight = height

        self.makeAssets()
    
    def makeAssets(self) -> None:
        """ Make all the stuff. """

        self.screenQuad = screen_quad.ScreenQuad()

        self.colorBuffer = material.Material(self.screenWidth, self.screenHeight)

        self.createResourceMemory()

        self.shader = self.createShader("shaders/frameBufferVertex.txt",
                                        "shaders/frameBufferFragment.txt")
        
        self.rayTracerShader = self.createComputeShader("shaders/rayTracer.txt")
    
    def createResourceMemory(self):

        self.objectData = np.zeros((32 * 8), dtype = np.float32)
        self.planeData = np.zeros((1 * 19), dtype=np.float32)

        self.objectDataBuffer = glGenBuffers(1)
        glBindBuffer(GL_SHADER_STORAGE_BUFFER, self.objectDataBuffer)
        glBufferData(GL_SHADER_STORAGE_BUFFER,self.objectData.nbytes, self.objectData, GL_DYNAMIC_READ)
        glBindBufferBase(GL_SHADER_STORAGE_BUFFER, 1, self.objectDataBuffer)
        
    def createShader(self, vertexFilepath, fragmentFilepath) -> int:
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
    
    def recordSphere(self, i, sphere):

        self.objectData[8*i]   = sphere.center[0]
        self.objectData[8*i+1] = sphere.center[1]
        self.objectData[8*i+2] = sphere.center[2]
        self.objectData[8*i+3] = sphere.radius
        self.objectData[8*i+4] = sphere.color[0]
        self.objectData[8*i+5] = sphere.color[1]
        self.objectData[8*i+6] = sphere.color[2]

    def recordObject(self, i, object):
        
        match object.type:
            case 1:
                self.objectData[8*i]   = object.center[0]
                self.objectData[8*i+1] = object.center[1]
                self.objectData[8*i+2] = object.center[2]
                self.objectData[8*i+3] = object.radius
                self.objectData[8*i+4] = object.color[0]
                self.objectData[8*i+5] = object.color[1]
                self.objectData[8*i+6] = object.color[2]

            case 2:
                self.objectData[8*i]   = object.center[0]
                self.objectData[8*i+1] = object.center[1]
                self.objectData[8*i+2] = object.center[2]

                self.objectData[8*i+3] = object.tangent[0]
                self.objectData[8*i+4] = object.tangent[1]
                self.objectData[8*i+5] = object.tangent[2]

                self.objectData[8*i+6] = object.bitangent[0]
                self.objectData[8*i+7] = object.bitangent[1]
                self.objectData[8*i+8] = object.bitangent[2]

                self.objectData[8*i+9]  = object.normal[0]
                self.objectData[8*i+10] = object.normal[1]
                self.objectData[8*i+11] = object.normal[2]

                self.objectData[8*i+12] = object.uMin
                self.objectData[8*i+13] = object.uMax
                self.objectData[8*i+14] = object.vMin
                self.objectData[8*i+15] = object.vMax

                self.objectData[8*i+16] = object.color[0]
                self.objectData[8*i+17] = object.color[1]
                self.objectData[8*i+18] = object.color[2]

    def createComputeShader(self, filepath) -> int:
        """
            Read source code, compile and link shaders.
            Returns the compiled and linked program.
        """

        with open(filepath,'r') as f:
            compute_src = f.readlines()
        
        shader = compileProgram(compileShader(compute_src, GL_COMPUTE_SHADER))
        
        return shader

    def updateScene(self, scene):
        scene.outDate = False

        glUseProgram(self.rayTracerShader)

        glUniform1f(glGetUniformLocation(self.rayTracerShader,"s_count"),len(scene.spheres))

        for i,sphere in enumerate(scene.spheres):
            self.recordSphere(i, sphere)

        glBindBuffer(GL_SHADER_STORAGE_BUFFER, self.objectDataBuffer)
        glBufferSubData(GL_SHADER_STORAGE_BUFFER,0, 8*4*len(scene.spheres),self.objectData)
        glBindBufferBase(GL_SHADER_STORAGE_BUFFER, 1, self.objectDataBuffer)
        

    def prepareScene(self,scene):
        glUseProgram(self.rayTracerShader)

        glUniform3fv(glGetUniformLocation(self.rayTracerShader,"viewer.position"),1,scene.camera.position)
        glUniform3fv(glGetUniformLocation(self.rayTracerShader,"viewer.forwards"),1,scene.camera.forwards)
        glUniform3fv(glGetUniformLocation(self.rayTracerShader,"viewer.right"),1,scene.camera.right)
        glUniform3fv(glGetUniformLocation(self.rayTracerShader,"viewer.up"),1,scene.camera.up)

        if scene.outDated:
            self.updateScene(scene)    

        k = 0
        for i,sphere in enumerate(scene.spheres):
            self.recordObject(i, sphere)

        self.recordObject(k,scene.plane)

        glBindBuffer(GL_SHADER_STORAGE_BUFFER, self.objectDataBuffer)
        glBufferSubData(GL_SHADER_STORAGE_BUFFER,0, 8*4*len(scene.spheres),self.objectData)
        glBindBufferBase(GL_SHADER_STORAGE_BUFFER, 1, self.objectDataBuffer)

    def renderScene(self,scene) -> None:
        """
            Draw all objects in the scene
        """
        
        glUseProgram(self.rayTracerShader)

        self.prepareScene(scene)

        self.colorBuffer.writeTo()
        
        glDispatchCompute(int(self.screenWidth/8), int(self.screenHeight/8), 1)
  
        # make sure writing to image has finished before read
        glMemoryBarrier(GL_SHADER_IMAGE_ACCESS_BARRIER_BIT)

        self.drawScreen()

    def drawScreen(self):
        glUseProgram(self.shader)
        glBindFramebuffer(GL_FRAMEBUFFER, 0)
        self.colorBuffer.readFrom()
        self.screenQuad.draw()
        pg.display.flip()
    
    def destroy(self):
        """
            Free any allocated memory
        """
        glDeleteProgram(self.rayTracerShader)
        self.screenQuad.destroy()
        self.colorBuffer.destroy()
        glDeleteProgram(self.shader)