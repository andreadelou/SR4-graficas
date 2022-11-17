import struct
from obj import Obj
from Vector import *

def char(c):
    # 1 byte
  return struct.pack('=c', c.encode('ascii'))


def word(w):
    # 2 bytes
    return struct.pack('=h', w)

def dword(d):
    # 4 bytes
    return struct.pack('=l',d)


def color(r,g,b):
    # Creacion de Color (255 deja usar todos los colores)
    return bytes([int(b*255),
                int(g*255),
                int(r*255)])



class Render(object):
    # Constructor
    def __init__(self):
        self.viewPortX = 0
        self.viewPortY = 0
        self.height = 0
        self.width = 0
        self.clearColor = color(0, 0, 0)

        self.current_color = color(1, 1, 1)
        self.framebuffer = []
       
        self.glViewport(0,0,self.width, self.height)
        self.glClear() 

    def glCreateWindow(self, width, height):
        self.width = width
        self.height = height
        self.glClear()

    def glViewport(self, x, y, width, height):
        self.viewpx = x
        self.viewpy = y
        self.viewpwidth = width
        self.viewpheight = height
    
    def glClear(self):
        self.framebuffer = [[self.clearColor for x in range(self.width+1)]
                            for y in range(self.height+1)]

    def glClearColor(self, r, g, b):
        self.clearColor = color(r, b, g)
        self.glClear()

    def glColor(self, r, g, b):
        self.current_color = color(r, g, b)

    def glPoint(self, x, y, color):
      self.framebuffer[int(round((x+1) * self.width / 2))][int(round((y+1) * self.height / 2))] = color

    def glLine(self,x1, y1, x2, y2):
      x1 = int(round((x1+1) * self.width / 2))
      y1 = int(round((y1+1) * self.height / 2))
      x2 = int(round((x2+1) * self.width / 2))
      y2 = int(round((y2+1) * self.height / 2))
      steep=(abs(y2 - y1))>(abs(x2 - x1))
      if steep:
        x1, y1 = y1, x1
        x2, y2 = y2, x2
      if x1>x2:
        x1,x2 = x2,x1
        y1,y2 = y2,y1

      dy = abs(y2 - y1)
      dx = abs(x2 - x1)
      y = y1
      offset = 0
      threshold = dx

      for x in range(x1, x2):
        if offset>=threshold:
          y += 1 if y1 < y2 else -1
          threshold += 2*dx
        if steep:
          self.framebuffer[x][y] = self.pintar
        else:
          self.framebuffer[y][x] = self.pintar
        offset += 2*dy
            
    def glObjModel(self, file_name, translate=(0,0), scale=(1,1)):
      model = Obj(file_name)
      model.read()
      
      for face in model.faces:
        vertices_ctr = len(face)
        for j in range(vertices_ctr):
          f1 = face[j][0]
          f2 = face[(j+1) % vertices_ctr][0]
          
          v1 = model.vertices[f1 - 1]
          v2 = model.vertices[f2 - 1]

          x1 = (v1[0] + translate[0]) * scale[0]
          y1 = (v1[1] + translate[1]) * scale[1]
          x2 = (v2[0] + translate[0]) * scale[0]
          y2 = (v2[1] + translate[1]) * scale[1]

          self.glLine(x1, y1, x2, y2)
                    
    # Función para crear la imagen
    def glFinish(self, filename):
        with open(filename, 'bw') as file:
            # Header
            file.write(bytes('B'.encode('ascii')))
            file.write(bytes('M'.encode('ascii')))

            # file size
            file.write(dword(14 + 40 + self.height * self.width * 3))
            file.write(dword(0))
            file.write(dword(14 + 40))

            # Info Header
            file.write(dword(40))
            file.write(dword(self.width))
            file.write(dword(self.height))
            file.write(word(1))
            file.write(word(24))
            file.write(dword(0))
            file.write(dword(self.width * self.height * 3))
            file.write(dword(0))
            file.write(dword(0))
            file.write(dword(0))
            file.write(dword(0))

            # Color table
            for y in range(self.height):
                for x in range(self.width):
                    file.write(self.framebuffer[x][y])
            file.close()
      

  
r = Render()
r.glCreateWindow(1000, 1000)
r.glViewport(int(0),int(0),int(1000/1), int(000/1))
r.glClear()


r.glObjModel('silla.obj', (0, 0), (0.3, 0.3))
r.glFinish("a.bmp")