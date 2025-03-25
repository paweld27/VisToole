#####################################################
#                                                   #
#   Shapes - AsTeR - tech@asterlab.pl               #
#   Paweł Dorobek                                   #
#                                                   #
#   ver. 0.900      - 01.2024                       #
#                                                   #
#   python     - 3.8.10                             #
#   matplotlib - 7.7.4                              #
#                                                   #
#####################################################

"""
Only individual 'get_position' and  'set_position' methods are added
tailored to the needs of the MoveXY class in the VisToole module.
If they are not to be moved, original patches can be used.
"""

from matplotlib.artist import Artist
import matplotlib.patches as patches
from matplotlib.transforms import Affine2D


class PointPatch:

    def get_position(self):
        return self.center

    def set_position(self, xy):
        self.set_center(xy)

    def jump_to_data(self):
        w = self.get_width()
        h = self.get_height()
        x, y = self.get_position()
        xw, yh = self.axes.transLimits.inverted().transform((x+w, y+h))        
        x, y = self.axes.transLimits.inverted().transform((x, y))
        self.set_width(xw-x)
        self.set_height(yh-y)
        self.set_position((x, y))

    def jump_to_axes(self):
        w = self.get_width()
        h = self.get_height()
        x, y = self.get_position()
        xw, yh = self.axes.transLimits.transform((x+w, y+h))
        x, y = self.axes.transLimits.transform((x, y))
        self.set_width(xw-x)
        self.set_height(yh-y) 
        self.set_position((x, y))


class Annulus(patches.Annulus, PointPatch):
    def __init__(self, xy, r, width, angle=0, **kwargs):
        super().__init__(xy, r, width, angle=angle, **kwargs)

        self.jumper = True  # can jump between domains

    def jump_to_data(self):
        w = self.get_width()
        r1, r2 = self.get_radii()
        x, y = self.get_position()
        r1, r2 = self.axes.transLimits.inverted().transform((x+r1, y+r2))
        x, y = self.axes.transLimits.inverted().transform((x, y))
        r1 -= x
        r2 -= y
        self.set_radii((r1, r2))
        self.set_position((x, y))

    def jump_to_axes(self):
        w = self.get_width()
        r1, r2 = self.get_radii()
        x, y = self.get_position()
        r1, r2 = self.axes.transLimits.transform((x+r1, y+r2))
        x, y = self.axes.transLimits.transform((x, y))
        r1 -= x
        r2 -= y
        self.set_radii((r1, r2))
        self.set_position((x, y))
 

class Ellipse(patches.Ellipse, PointPatch):
    def __init__(self, xy, width, height, angle=0, **kwargs):
        super().__init__(xy, width, height, angle=angle, **kwargs)

        self.jumper = True  # can jump between domains


class Circle(patches.Circle, PointPatch):
    def __init__(self, xy, radius, **kwargs):
        super().__init__(xy, radius=radius, **kwargs)

        self.jumper = True  # can jump between domains


class Wedge(patches.Wedge, PointPatch):
    def __init__(self, center, r, theta1, theta2, *, width=None, **kwargs):
        super().__init__(center, r, theta1, theta2, width=width, **kwargs)

        self._angle = 0 # degree

    def set_angle(self, angle):

        self.set_theta1(self.theta1+angle-self._angle)
        self.set_theta2(self.theta2+angle-self._angle)
        
        self._angle = angle


    def get_angle(self):
        """Return the angle of the ellipse."""
        return self._angle

    angle = property(get_angle, set_angle)

        

class Rectangle(patches.Rectangle, PointPatch):
    def __init__(self, xy, width, height, angle=0, *,
                 rotation_point='xy', **kwargs):
        super().__init__(xy, width, height, angle,
                         rotation_point=rotation_point, **kwargs)

        self.jumper = True  # can jump between domains
    
    def get_position(self):
        return self.get_xy()
    
    def set_position(self, xy):
        self.set_xy(xy)

        
class Polygon(patches.Polygon):
    def __init__(self, xy, closed=True, angle=0, **kwargs):
        super().__init__(xy, closed=closed, **kwargs)

        self.jumper = True  # can jump between domains
        
        # dxy it's a numpy array of distances between
        # vertex_0 and every other vertex
        self.dxy = self.get_xy() - self.get_xy()[0]
        self._angle = 0
        self.set_angle(angle) # degree
    
    def get_position(self):
        return self.get_xy()[0].tolist()
    
    def set_position(self, xy):
        self.set_xy(self.dxy + xy)

    def jump_to_data(self):
        xy = self.get_xy()
        for i in range(len(xy)):
            xy[i] = self.axes.transLimits.inverted().transform(xy[i])
        self.set_xy(xy)
        self.dxy = self.get_xy() - self.get_xy()[0]
    
    def jump_to_axes(self):
        xy = self.get_xy()
        for i in range(len(xy)):
            xy[i] = self.axes.transLimits.transform(xy[i])
        self.set_xy(xy)
        self.dxy = self.get_xy() - self.get_xy()[0]

    def set_angle(self, angle):

        p0 = self.get_position()
        self.set_xy(Affine2D().rotate_deg(angle-self._angle) \
                              .transform(self.dxy) + p0)
        
        self.dxy = self.get_xy() - self.get_xy()[0]
        self._angle = angle


    def get_angle(self):
        """Return the angle of the ellipse."""
        return self._angle

    angle = property(get_angle, set_angle)

    
class FancyArrow(patches.FancyArrow, Polygon):
    """
    !!! not finished yet !!!
    """
    
    def __init__(self, x, y, dx, dy, width=0.001, **kwargs):
        super().__init__(x, y, dx, dy, width=0.001, **kwargs)

        self.jumper = True  # can jump between domains
    
    def get_position(self):
        return self.get_xy()
    
    def set_position(self, xy):
        self.set_xy(xy)
       

    

        
