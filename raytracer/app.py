from config import *
import engine
import scene

class App:
    """
        Calls high level control functions (handle input, draw scene etc)
    """

    def __init__(self):

        
        self.screenWidth = 1920
        self.screenHeight = 1080
        self.setupPygame()

        self.graphicsEngine = engine.Engine(self.screenWidth, self.screenHeight)
        self.scene = scene.Scene()

        self.setupTimer()

        self.mainLoop()

    def setupPygame(self) -> None:
        """ Set up pygame. """

        pg.init()
        pg.display.gl_set_attribute(pg.GL_CONTEXT_MAJOR_VERSION, 4)
        pg.display.gl_set_attribute(pg.GL_CONTEXT_MINOR_VERSION, 3)
        pg.display.gl_set_attribute(pg.GL_CONTEXT_PROFILE_MASK,
                                    pg.GL_CONTEXT_PROFILE_CORE)
        pg.display.set_mode((self.screenWidth, self.screenHeight), pg.OPENGL|pg.DOUBLEBUF)
        pg.mouse.set_visible(False)
    
    def setupTimer(self) -> None:
        """
            set up the framerate timer
        """

        self.lastTime = pg.time.get_ticks()
        self.currentTime = pg.time.get_ticks()
        self.numFrames = 0
        self.frameTime = 0
    
    def mainLoop(self) -> None:
        """ Run the program """

        running = True
        while (running):
            #events
            for event in pg.event.get():
                if (event.type == pg.QUIT):
                    running = False
                if (event.type == pg.KEYDOWN):
                    if (event.key == pg.K_ESCAPE):
                        running = False
                if (event.type == pg.K_w):
                    scene.camera.position[0] += 2
                if (event.type == pg.K_s):
                    scene.camera.position[0] -= 2
                if (event.type == pg.K_d):
                    scene.camera.position[1] += 2
                if (event.type == pg.K_a):
                    scene.camera.position[1] -= 2
            
            #render
            self.graphicsEngine.renderScene(self.scene)

            self.handleKeys()
            #self.handleMouse()

            #timing
            self.calculateFramerate()
        self.quit()

    def handleKeys(self):

        rate = self.frameTime / 16

        keys = pg.key.get_pressed()

        if keys[pg.K_w]:
            self.scene.move_player(0.1 * rate, 0)
        elif keys[pg.K_a]:
            self.scene.move_player(0, -0.1*rate)
        elif keys[pg.K_s]:
            self.scene.move_player(-0.1 * rate, 0)
        elif keys[pg.K_d]:
            self.scene.move_player(0, 0.1*rate)
        elif keys[pg.K_LEFT]:
            phi_increment =   self.frameTime* 0.0005 *((self.screenHeight//2))
            self.scene.spin_player((0,phi_increment))
        elif keys[pg.K_RIGHT]:
            phi_increment =   self.frameTime* 0.0005 * -1 *((self.screenHeight//2))
            self.scene.spin_player((0,phi_increment))
        elif keys[pg.K_UP]:
            theta_increment = self.frameTime* 0.0005 * -1 *((self.screenWidth//2))
            self.scene.spin_player((theta_increment,0))
        elif keys[pg.K_DOWN]:
            theta_increment = self.frameTime* 0.0005 *((self.screenWidth//2))
            self.scene.spin_player((theta_increment,0))
            

    def handleMouse(self):

        (x,y) = pg.mouse.get_pos()

        theta_increment = self.frameTime* 0.05 *((self.screenWidth//2)-x)
        phi_increment =   self.frameTime* 0.05 *((self.screenHeight//2)-y)
        self.scene.spin_player((theta_increment,phi_increment))
        pg.mouse.set_pos((self.screenWidth//2,self.screenHeight//2))


    
    def calculateFramerate(self) -> None:
        """
            Calculate the framerate of the program.
        """

        self.currentTime = pg.time.get_ticks()
        delta = self.currentTime - self.lastTime
        if (delta >= 1000):
            framerate = max(1,int(1000.0 * self.numFrames/delta))
            pg.display.set_caption(f"Running at {framerate} fps.")
            self.lastTime = self.currentTime
            self.numFrames = -1
            self.frameTime = float(1000.0 / max(1,framerate))
        self.numFrames += 1

    def quit(self) -> None:
        """
            For some reason, the graphics engine's destructor throws weird errors.
        """
        #self.graphicsEngine.destroy()
        pg.quit()