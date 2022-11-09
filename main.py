import struct
from obj import Obj
from Vector import *

def char(c):
  return struct.pack('=c', c.encode('ascii'))

def word(w):
  return struct.pack('=h', w)

def dword(d):
  return struct.pack('=l', d)

def color(r, g, b):
    return bytes([b, g, r])
  
def color_unit(r, g, b):
  return color(clamping(r*255), clamping(g*255), clamping(b*255))
  
def clamping(num):
  return int(max(min(num, 255), 0))
    
class Render(object):
  def __init__(self, width, height):
    self.pintar = color(255,255,255)
    self.framebuffer = []
  
    self.width = width
    self.height = height
    self.XViewPort= 0
    self.YViewPort= 0
    self.widthVP = 0
    self.heightVP = 0
    
    self.clearColor = color(0, 0, 0)
    self.current_color = color(1,0,0)
    
    

    self.glViewPort(0,0,self.width, self.height)
    self.glClear()

  def glClear(self):
    self.framebuffer = [
      [color(0,0,0) for x in range(self.width)] 
      for y in range(self.height)
    ]

  def glCreateWindow(self,width, height):
      self.width = width
      self.height = height
    
  def glViewPort(self, x, y, width, height):
      self.XViewPort= x
      self.YViewPort= y
      self.widthVP= width
      self.heightVP= height
      
  def glClearColor(self, r, g, b):
      self.clearColor = color(r, b, g)
      self.glClear()
      
  def glColor(self, r, g, b):
      self.current_color = color(r, g, b)
            
  def glVertex(self, x, y):
      puntoX = round( (x+1) * (self.widthVP/ 2 )  + self.XViewPort)
      puntoY = round( (y+1) * (self.heightVP / 2) + self.YViewPort)
      
      self.framebuffer[puntoY][puntoX] = color(1,1,1)
    
 
              
  def glFinish(self, filename):
    f = open(filename, 'bw')

    # File header (14 bytes)
    f.write(char('B'))
    f.write(char('M'))
    f.write(dword(14 + 40 + self.width * self.height * 3))
    f.write(dword(0))
    f.write(dword(14 + 40))

    # Image header (40 bytes)
    f.write(dword(40))
    f.write(dword(self.width))
    f.write(dword(self.height))
    f.write(word(1))
    f.write(word(24))
    f.write(dword(0))
    f.write(dword(self.width * self.height * 3))
    f.write(dword(0))
    f.write(dword(0))
    f.write(dword(0))
    f.write(dword(0))

    # Pixel data (width x height x 3 pixels)
    for x in range(self.height):
      for y in range(self.width):
        f.write(self.framebuffer[x][y])

    f.close()

  def point(self, x, y, color = None):
    # 0,0 was intentionally left in the bottom left corner to mimic opengl
    self.pixels[y][x] = color or self.current_color
    
  def set_color(self, color):
    self.current_color = color
    
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
  
  #SR3
  def glObjModel(self, file_name, translate=(0,0), scale=(1,1)):
        #Lector .obj
        model = Obj(file_name)
        
        for face in model.faces:
            if len(face) == 3:

                v1 = self.transform(model.vertices[face[0][0] - 1], translate, scale)
                v2 = self.transform(model.vertices[face[1][0] - 1], translate, scale)
                v3 = self.transform(model.vertices[face[2][0] - 1], translate, scale)

                self.trainglebb(v1, v2, v3)
            if len(face) == 4:

                f1 = face[0][0] - 1
                f2 = face[1][0] - 1
                f3 = face[2][0] - 1
                f4 = face[3][0] - 1

                vertices = [
                    self.transform(model.vertices[f1], translate, scale),
                    self.transform(model.vertices[f2], translate, scale),
                    self.transform(model.vertices[f3], translate, scale),
                    self.transform(model.vertices[f4], translate, scale)
                ]

                A, B, C, D = vertices

                self.trainglebb(A, B, C)
                self.trainglebb(A, C, D)
  
  #SR4 
  def cross(self, v1, v2):
    return (
        v1.y * v2.z - v1.z * v2.y,
        v1.z * v2.x - v1.x * v2.z,
        v1.x * v2.y - v1.y * v2.x
    )
  
  def bounding_box(self, A, B, C):
    coordenadas = [(A.x, A.y),(B.x, B.y),(C.x, C.y)]

    xmin = 999999
    xmax = -999999
    ymin = 999999
    ymax = -999999

    for (x, y) in coordenadas:
        if x < xmin:
            xmin = x
        if x > xmax:
            xmax = x
        if y < ymin:
            ymin = y
        if y > ymax:
            ymax = y
    return V3(xmin, ymin), V3(xmax, ymax)
  
  def barycentric(self, A, B, C, P):
    
    cx, cy, cz = cross(
        V3(B.x - A.x, C.x - A.x, A.x - P.x),
        V3(B.y - A.y, C.y - A.y, A.y - P.y)
    )
    
    if abs(cz) < 1:
        return(-1, -1, -1)
      
    u = cx / cz
    v = cy / cz
    w = 1 - (u + v) 

    return (w, v, u)
  
  def transform(self, vertex, translate, scale):
        return V3(
            ((vertex[0] * scale[0]) + translate[0]),
            ((vertex[1] * scale[1]) + translate[1]),
            ((vertex[2] * scale[2]) + translate[2])
        )
  
  def lightPosition(self, x:int, y:int, z:int):
        self.light = V3(x, y, z)
        
  def trainglebb(self, vertices, tvertices=()):
        A, B, C = vertices
        if self.texture:
            tA, tB, tC = tvertices
        
        Light = self.light
        Normal = (B - A) * (C - A)
        i = Normal.norm() @ Light.norm()
        if i < 0:
            return

        print(i)
        self.clearColor = color_select(
            round(255 * i),
            round(255 * i),
            round(255 * i)
        )

        min,max = bounding_box(A, B, C)
        min.round_coords()
        max.round_coords()
        
        for x in range(min.x, max.x + 1):
            for y in range(min.y, max.y + 1):
                w, v, u = barycentric(A, B, C, V3(x, y))

                if (w < 0 or v < 0 or u < 0):
                    continue

                z = A.z * w + B.z * v + C.z * u
                if (self.zBuffer[x][y] < z):
                    self.zBuffer[x][y] = z

                    if self.texture:
                        tx = tA.x * w + tB.x * u + tC.x * v
                        ty = tA.y * w + tB.y * u + tC.y * v

                        self.current_color = self.texture.get_color_with_intensity(tx, ty, i)
                    
                    self.glPoint(x, y)
  
    
r = Render(400,400)
r.glCreateWindow(400, 400)
r.glViewPort(400,400 , 400, 400)
r.lightPosition(0, 0, 1)
r.glObjModel('silla.obj', (500, 10, 0), (200, 200, 200))

r.glFinish("obj.bmp")