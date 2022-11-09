class V3(object):
    # creacion del vector en 3D
    def __init__(self, x, y, z=0):
        self.x = x
        self.y = y
        self.z = z

    # suma
    def __add__(self, other):
        return V3(
            self.x + other.x,
            self.y + other.y,
            self.z + other.z
        )

    # resta
    def __sub__(self, other):
        return V3(
            self.x - other.x,
            self.y - other.y,
            self.z - other.z
        )

    # multiplicacion
    def __mul__(self, other):
        # si es escalar
        if (type(other) == int or type(other) == float):
            return V3(
                self.x * other,
                self.y * other,
                self.z * other
            )
        # si es vector retorna el producto cruz
        return V3(
            self.y * other.z - self.z * other.y,
            self.z * other.x - self.x * other.z,
            self.x * other.y - self.y * other.x
        )

    # producto punto
    def __matmul__(self, other):
        return self.x * other.x + self.y * other.y + self.z * other.z

    # magnitud de un vector
    def length(self):
        return (self.x**2 + self.y**2 + self.z**2)**0.5

    def norm(self):
        return self * (1/self.length())

    # print bonito
    def __repr__(self):
        return "V3 (%s, %s, %s)" % (self.x, self.y, self.z)