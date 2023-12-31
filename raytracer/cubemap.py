from config import * 

class CubeMap:

    def __init__(self, filepath):
        
        self.texture = glGenTextures(1)
        glBindTexture(GL_TEXTURE_CUBE_MAP, self.texture)

        glTexParameteri(GL_TEXTURE_CUBE_MAP,GL_TEXTURE_WRAP_S,GL_CLAMP_TO_EDGE)
        glTexParameteri(GL_TEXTURE_CUBE_MAP,GL_TEXTURE_WRAP_T,GL_CLAMP_TO_EDGE)
        glTexParameteri(GL_TEXTURE_CUBE_MAP,GL_TEXTURE_WRAP_R,GL_CLAMP_TO_EDGE)
        glTexParameteri(GL_TEXTURE_CUBE_MAP,GL_TEXTURE_MIN_FILTER,GL_NEAREST)
        glTexParameteri(GL_TEXTURE_CUBE_MAP,GL_TEXTURE_MAG_FILTER,GL_LINEAR)

        filenames = ["Back-Z","Front+Z","Right-X","Left+X","Down-Y","Up+Y"]
        constants = [GL_TEXTURE_CUBE_MAP_NEGATIVE_Z,GL_TEXTURE_CUBE_MAP_POSITIVE_Z,GL_TEXTURE_CUBE_MAP_NEGATIVE_X,GL_TEXTURE_CUBE_MAP_POSITIVE_X,GL_TEXTURE_CUBE_MAP_NEGATIVE_Y,GL_TEXTURE_CUBE_MAP_POSITIVE_Y]

        for i in range(len(filenames)):
            with Image.open(f"textures\\{filepath}\\Nebula_{filenames[i]}.png", mode = "r") as img:
                width,height = img.size
                if i == 2:
                    img = ImageOps.flip(img)
                    img = ImageOps.mirror(img)
                elif img == 5:
                    img = img.rotate(90)
                elif img == 0:
                    img = img.rotate(90)
                elif img == 1:
                    img = img.rotate(-90)
                elif img == 4:
                    img = img.rotate(90)
                img = img.convert("RGBA")
                img_data = bytes(img.tobytes())
                #img.save(f"intermediate_{i}_{j}.png")
                glTexImage2D(constants[i],0,GL_RGBA8,width,height,0,GL_RGBA,GL_UNSIGNED_BYTE,img_data)
        
    def use(self):
        glActiveTexture(GL_TEXTURE6)
        glBindTexture(GL_TEXTURE_CUBE_MAP,self.texture)

    def destroy(self):
        glDeleteTextures(1,(self.texture,))