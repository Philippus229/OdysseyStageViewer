import pygame, os
from OpenGL.GL import *
from math import *

def math_sin(x):
    return sin((x*pi)/180)

def math_cos(x):
    return cos((x*pi)/180)

def MTL(filename):
    contents = {}
    mtl = None
    for line in open(filename, "r"):
        if line.startswith('#'): continue
        values = line.split()
        if not values: continue
        if values[0] == 'newmtl':
            mtl = contents[values[1]] = {}
        elif mtl is None:
            print("mtl file doesn't start with newmtl stmt")
        elif values[0] == 'map_Kd':
            mtl[values[0]] = values[1]
            surf = None
            try:
                surf = pygame.image.load(os.path.join("models", mtl['map_Kd']))
            except:
                surf = pygame.image.load("missing.bmp")
            image = pygame.image.tostring(surf, 'RGBA', 1)
            ix, iy = surf.get_rect().size
            texid = mtl['texture_Kd'] = glGenTextures(1)
            glBindTexture(GL_TEXTURE_2D, texid)
            glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER,
                GL_LINEAR)
            glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER,
                GL_LINEAR)
            glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, ix, iy, 0, GL_RGBA,
                GL_UNSIGNED_BYTE, image)
        else:
            mtl[values[0]] = list(map(float, values[1:]))
    return contents

class OBJ:
    def __init__(self, filename, obj_data):
        self.vertices = []
        self.normals = []
        self.texcoords = []
        self.faces = []
        material = None
        for line in open(filename, "r"):
            if line.startswith('#'): continue
            values = line.split()
            if not values: continue
            if values[0] == 'v':
                v = list(map(float, values[1:4]))
                '''Old code without rotation that works:'''
                v = [v[0]*obj_data[2][0]+obj_data[0][0],
                     v[1]*obj_data[2][1]+obj_data[0][1],
                     v[2]*obj_data[2][2]+obj_data[0][2]]
                
                '''New code that I need to fix:
                tX = math_cos(obj_data[1][1])*v[0]-math_sin(obj_data[1][1])*v[2]
                tZ = math_cos(obj_data[1][1])*v[2]+math_sin(obj_data[1][1])*v[0]
                tY = math_sin(obj_data[1][0])*tZ-math_cos(obj_data[1][0])*v[1]
                tZ = math_cos(obj_data[1][0])*tZ+math_sin(obj_data[1][0])*v[1]
                tY2 = tY
                tY = math_sin(obj_data[1][2])*tX+math_cos(obj_data[1][2])*tY
                tX = math_cos(obj_data[1][2])*tX-math_sin(obj_data[1][2])*tY2
                v = [(tX*obj_data[2][0]+obj_data[0][0]),
                     (-tY*obj_data[2][1]+obj_data[0][1]),
                     (tZ*obj_data[2][2]+obj_data[0][2])]
                '''
                self.vertices.append(v)
            elif values[0] == 'vn':
                v = list(map(float, values[1:4]))
                '''Old code without rotation that works:'''
                v = [v[0]*obj_data[2][0]+obj_data[0][0],
                     v[1]*obj_data[2][1]+obj_data[0][1],
                     v[2]*obj_data[2][2]+obj_data[0][2]]
                
                '''New code that I need to fix:
                tX = math_cos(obj_data[1][1])*v[0]-math_sin(obj_data[1][1])*v[2]
                tZ = math_cos(obj_data[1][1])*v[2]+math_sin(obj_data[1][1])*v[0]
                tY = math_sin(obj_data[1][0])*tZ-math_cos(obj_data[1][0])*v[1]
                tZ = math_cos(obj_data[1][0])*tZ+math_sin(obj_data[1][0])*v[1]
                tY2 = tY
                tY = math_sin(obj_data[1][2])*tX+math_cos(obj_data[1][2])*tY
                tX = math_cos(obj_data[1][2])*tX-math_sin(obj_data[1][2])*tY2
                v = [(tX*obj_data[2][0]+obj_data[0][0]),
                     (-tY*obj_data[2][1]+obj_data[0][1]),
                     (tZ*obj_data[2][2]+obj_data[0][2])]
                '''
                self.normals.append(v)
            elif values[0] == 'vt':
                self.texcoords.append(list(map(float, values[1:3])))
            elif values[0] in ('usemtl', 'usemat'):
                material = values[1]
            elif values[0] == 'mtllib':
                self.mtl = MTL(os.path.join("models", values[1]))
            elif values[0] == 'f':
                face = []
                texcoords = []
                norms = []
                for v in values[1:]:
                    w = v.split('/')
                    face.append(int(w[0]))
                    if len(w) >= 2 and len(w[1]) > 0:
                        texcoords.append(int(w[1]))
                    else:
                        texcoords.append(0)
                    if len(w) >= 3 and len(w[2]) > 0:
                        norms.append(int(w[2]))
                    else:
                        norms.append(0)
                self.faces.append((face, norms, texcoords, material))
        self.gl_list = glGenLists(1)
        glNewList(self.gl_list, GL_COMPILE)
        glEnable(GL_TEXTURE_2D)
        glFrontFace(GL_CCW)
        for face in self.faces:
            vertices, normals, texture_coords, material = face
            try:
                mtl = self.mtl[material]
                if 'texture_Kd' in mtl:
                    glBindTexture(GL_TEXTURE_2D, mtl['texture_Kd'])
                else:
                    glColor(*mtl['Kd'])
                glBegin(GL_POLYGON)
            except:
                print("Material not found: " + material)
            for i in range(len(vertices)):
                if normals[i] > 0:
                    glNormal3fv(self.normals[normals[i] - 1])
                if texture_coords[i] > 0:
                    glTexCoord2fv(self.texcoords[texture_coords[i] - 1])
                glVertex3fv(self.vertices[vertices[i] - 1])
            glEnd()
        glDisable(GL_TEXTURE_2D)
        glEndList()

class OBJ_test:
    def __init__(self, filename, obj_data):
        self.pos = obj_data[0]
        self.rot = obj_data[1]
        self.scale = obj_data[2]
        self.obj = OBJ(filename, obj_data)
