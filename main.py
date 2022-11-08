import struct
from obj import Obj

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
  
  def glObjModel(self, file_name, translate=(0,0), scale=(1,1)):
        #Lector .obj
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
    
r = Render(400,400)
r.glCreateWindow(400, 400)
r.glViewPort(400,400 , 400, 400)
r.glObjModel('silla.obj', (0, 0), (0.3, 0.3))

r.glFinish("obj.bmp")