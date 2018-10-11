from math import *
from objloader_new import *
from OpenGL.GL import *
from OpenGL.GLU import *
from pygame.locals import *
from pygame.constants import *
from SARCExtract import SARCExtract
from bntx_extract import bntx_extract
from tkinter.filedialog import askdirectory, askopenfilename
import embed_extract
import subprocess
import shutil
import pygame
import ntpath
import time
import byml
import sys
import os

def math_sin(x):
    return sin((x*pi)/180)

def math_cos(x):
    return cos((x*pi)/180)

def get_model_obj(modelname):
    obj_path = os.path.join("models", modelname + ".obj")
    romfs_dir = open("data0.txt", "r").read()
    new_data = []
    with open("data1.txt", "r") as f:
        for line in f.readlines():
            new_data.append(line)
            if line.replace('\n', '') == modelname:
                return obj_path
    szs_path = os.path.join(os.path.join(romfs_dir, "ObjectData"), modelname + ".szs")
    if os.path.isfile(szs_path):
        done = SARCExtract.extract_szs(szs_path)
        bfres_path = os.path.join(szs_path[:-4], modelname + ".bfres")
        done = subprocess.Popen(os.path.join("BFRES2OBJ", "BFRES2OBJ.exe") + " " + bfres_path + " " + os.path.join("models", modelname + ".obj"), stdout=subprocess.PIPE, shell=True).wait()
        new_lines = []
        if os.path.isfile(obj_path):
            with open(obj_path, "r") as f:
                for line in f.readlines():
                    new_lines.append(line.replace(",", "."))
            with open(obj_path, "w") as f:
                for line in new_lines:
                    f.write(line)
        with open("data1.txt", "w") as f:
            f.truncate(0)
            for line in new_data:
                if not line == "":
                    f.write(line)
            f.write(modelname + "\n")
        return obj_path
    return ""

def init_editor():
    if os.path.isdir("models"):
        with open("data0.txt", "r") as f:
            romfs_dir = f.read()
    else:
        os.mkdir("models")
        os.mkdir(os.path.join("models", "tex"))
        romfs_dir = askdirectory(title="Select a SMO RomFS dump")
        with open("data0.txt", "w") as f:
            f.write(romfs_dir)
        with open("data1.txt", "w") as f:
            f.write("")
        if os.path.isdir(romfs_dir):
            print("Extracting textures... (this will take a few minutes)")
            objdata_dir = os.path.join(romfs_dir, "ObjectData")
            if os.path.isdir(objdata_dir):
                for file in os.listdir(objdata_dir):
                    if file.endswith("Texture.szs"):
                        szs_path = os.path.join(objdata_dir, file)
                        done = SARCExtract.extract_szs(szs_path)
                        efd = szs_path[:-4]
                        if os.path.isdir(efd):
                            i = 0
                            while i < 2:
                                for file2 in os.listdir(efd):
                                    file_path = os.path.join(efd, file2)
                                    if file2.endswith(".bfres") and i == 0:
                                        done = embed_extract.extract_files(file_path)
                                    elif file2.endswith(".bntx") and i == 1:
                                        out_dir = os.path.join("models", "tex")
                                        done = bntx_extract.extract_textures(file_path, out_dir)
                                i += 1
                        shutil.rmtree(os.path.join(objdata_dir, file[:-4]))
                for file in os.listdir(os.path.join("models", "tex")):
                    if file.endswith(".dds"):
                        inf = os.path.join(os.path.join("models", "tex"), file)
                        command = "texconv.exe " + inf + " -o " + os.path.join("models", "tex") + " -ft bmp"
                        done = subprocess.Popen(command, stdout=subprocess.PIPE, shell=True).wait()
                        os.remove(inf)
            print("Done!")

def load_stage():
    tmp_objs = []
    stage_file_szs = askopenfilename(filetypes =(("SZS File", "*.szs"),("All Files","*.*")), title = "Select a SMO stage SZS")
    done = SARCExtract.extract_szs(stage_file_szs)
    stage_file = os.path.join(stage_file_szs[:-4], ntpath.basename(stage_file_szs)[:-3] + "byml")
    scenario = 0
    root = byml.Byml(open(stage_file, "rb").read()).parse()
    a = root[scenario]
    for b in a['ObjectList']:
        obj_name = ''
        stage_name = ''
        res_path = ''
        unit_cfg_name = ''
        obj_data = [[0,0,0],[0,0,0],[0,0,0]]
        for c in b:
            if c == 'ModelName':
                obj_name = str(b['ModelName'])
            elif c == 'PlacementFilename':
                stage_name = str(b['PlacementFilename'])
            elif c == 'ResourceCategory':
                res_path = str(b['ResourceCategory'])
            elif c == 'UnitConfigName':
                unit_cfg_name = str(b['UnitConfigName'])
            elif c == 'Translate':
                obj_data[0][0] = float(str(b['Translate']['X']).replace(',', '.'))
                obj_data[0][1] = float(str(b['Translate']['Y']).replace(',', '.'))
                obj_data[0][2] = float(str(b['Translate']['Z']).replace(',', '.'))
            elif c == 'Rotate':
                obj_data[1][0] = float(str(b['Rotate']['X']).replace(',', '.'))
                obj_data[1][1] = float(str(b['Rotate']['Y']).replace(',', '.'))
                obj_data[1][2] = float(str(b['Rotate']['Z']).replace(',', '.'))
            elif c == 'Scale':
                obj_data[2][0] = float(str(b['Scale']['X']).replace(',', '.'))
                obj_data[2][1] = float(str(b['Scale']['Y']).replace(',', '.'))
                obj_data[2][2] = float(str(b['Scale']['Z']).replace(',', '.'))
        if not obj_name == "":
            obj_path = get_model_obj(obj_name)
        if obj_path == "" or not os.path.isfile(obj_path):
            obj_path = get_model_obj(unit_cfg_name)
        print(obj_name)
        print(unit_cfg_name)
        if os.path.isfile(obj_path):
            tmp_objs.append(OBJ_test(obj_path, obj_data))
    print('Done!')
    return tmp_objs

def calc_pos_rtc(pos, rot):
    v0 = (math_cos(-rot[1])*pos[0])-(math_sin(-rot[1])*pos[2]);
    v2 = (math_cos(-rot[1])*pos[2])+(math_sin(-rot[1])*pos[0]);
    v1 = -((math_cos(-rot[0])*pos[1])-(math_sin(-rot[0])*v2));
    v2 = (math_cos(-rot[0])*v2)+(math_sin(-rot[0])*pos[1]);
    return [v0,v1,v2]

def test():
    pygame.init()
    viewport = (800,600)
    hx = viewport[0]/2
    hy = viewport[1]/2
    srf = pygame.display.set_mode(viewport, OPENGL | DOUBLEBUF)
    glLightfv(GL_LIGHT0, GL_POSITION,  (0, 0, 0, 0.0))
    glLightfv(GL_LIGHT0, GL_AMBIENT, (0.5, 0.5, 0.5, 1.0))
    glLightfv(GL_LIGHT0, GL_DIFFUSE, (0.5, 0.5, 0.5, 1.0))
    glEnable(GL_LIGHT0)
    glEnable(GL_LIGHTING)
    glEnable(GL_COLOR_MATERIAL)
    glEnable(GL_DEPTH_TEST)
    glShadeModel(GL_SMOOTH)
    objects = load_stage()
    clock = pygame.time.Clock()
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    width, height = viewport
    gluPerspective(90.0, width/float(height), 1, 1000000.0)
    glEnable(GL_DEPTH_TEST)
    glMatrixMode(GL_MODELVIEW)
    cam_data = [[0,0,0],[0,0,0]]
    speed = 100
    rotate = False
    move = False
    running = True
    while running:
        clock.tick(30)
        for e in pygame.event.get():
            if e.type == QUIT:
                running = False
            elif e.type == MOUSEBUTTONDOWN:
                if e.button == 4:
                    cam_data[0][0] += speed*(math_sin(-cam_data[1][1])-(math_sin(-cam_data[1][1])*math_sin(-cam_data[1][0])))
                    cam_data[0][1] += speed*(math_sin(-cam_data[1][0]))
                    cam_data[0][2] += speed*(math_cos(-cam_data[1][1])-(math_cos(-cam_data[1][1])*math_sin(-cam_data[1][0])))
                elif e.button == 5:
                    cam_data[0][0] -= speed*(math_sin(-cam_data[1][1])-(math_sin(-cam_data[1][1])*math_sin(-cam_data[1][0])))
                    cam_data[0][1] -= speed*(math_sin(-cam_data[1][0]))
                    cam_data[0][2] -= speed*(math_cos(-cam_data[1][1])-(math_cos(-cam_data[1][1])*math_sin(-cam_data[1][0])))
                elif e.button == 1: rotate = True
                elif e.button == 3: move = True
            elif e.type == MOUSEBUTTONUP:
                if e.button == 1: rotate = False
                elif e.button == 3: move = False
            elif e.type == MOUSEMOTION:
                mx, my = e.rel
                if rotate:
                    cam_data[1][0] += my
                    cam_data[1][1] += mx
                #if move:
                    #tx += mx*50
                    #ty -= my*50
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glLoadIdentity()
        tmp_thing = calc_pos_rtc(cam_data[0], cam_data[1])
        glTranslate(tmp_thing[0], tmp_thing[1], tmp_thing[2])
        glRotate(cam_data[1][0], 1, 0, 0)
        glRotate(cam_data[1][1], 0, 1, 0)
        for tmp_obj in objects:
            glCallList(tmp_obj.obj.gl_list)
        pygame.display.flip()
    pygame.quit()

init_editor()
test()
